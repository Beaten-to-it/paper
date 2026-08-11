const CONTAINER_FIELDS = [
  "version",
  "algorithm",
  "kdf",
  "iterations",
  "salt",
  "iv",
  "ciphertext",
];

const textEncoder = new TextEncoder();
const MAX_PBKDF2_ITERATIONS = 2_000_000;

function requireCrypto() {
  if (!globalThis.crypto?.subtle || !globalThis.crypto?.getRandomValues) {
    throw new Error("Web Crypto API is unavailable");
  }
  return globalThis.crypto;
}

function bytesToBase64(bytes) {
  let binary = "";
  for (let offset = 0; offset < bytes.length; offset += 0x8000) {
    binary += String.fromCharCode(...bytes.subarray(offset, offset + 0x8000));
  }
  return btoa(binary);
}

function base64ToBytes(value, label) {
  if (
    typeof value !== "string"
    || value.length === 0
    || value.length % 4 !== 0
    || !/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(value)
  ) {
    throw new Error(`invalid ${label} base64`);
  }
  let binary;
  try {
    binary = atob(value);
  } catch (error) {
    throw new Error(`invalid ${label} base64`, {cause: error});
  }
  const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
  if (bytesToBase64(bytes) !== value) {
    throw new Error(`invalid ${label} base64`);
  }
  return bytes;
}

function validateContainer(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("encrypted container must be an object");
  }
  const fields = Object.keys(value).sort();
  const expected = [...CONTAINER_FIELDS].sort();
  if (fields.length !== expected.length || fields.some((field, index) => field !== expected[index])) {
    throw new Error("invalid container fields");
  }
  if (value.version !== 1) {
    throw new Error("unsupported container version");
  }
  if (value.algorithm !== "AES-256-GCM") {
    throw new Error("unsupported encryption algorithm");
  }
  if (value.kdf !== "PBKDF2-HMAC-SHA-256") {
    throw new Error("unsupported key derivation function");
  }
  if (
    !Number.isSafeInteger(value.iterations)
    || value.iterations < 600_000
    || value.iterations > MAX_PBKDF2_ITERATIONS
  ) {
    throw new Error("invalid PBKDF2 iterations");
  }
  const salt = base64ToBytes(value.salt, "salt");
  const iv = base64ToBytes(value.iv, "iv");
  const ciphertext = base64ToBytes(value.ciphertext, "ciphertext");
  if (salt.length !== 16) {
    throw new Error("invalid salt length");
  }
  if (iv.length !== 12) {
    throw new Error("invalid iv length");
  }
  if (ciphertext.length < 17) {
    throw new Error("invalid ciphertext length");
  }
  return {container: {...value}, salt, iv, ciphertext};
}

async function deriveKey(password, salt, iterations, usages) {
  if (typeof password !== "string" || password.length === 0) {
    throw new Error("password is required");
  }
  const webCrypto = requireCrypto();
  const material = await webCrypto.subtle.importKey(
    "raw",
    textEncoder.encode(password),
    "PBKDF2",
    false,
    ["deriveKey"],
  );
  return webCrypto.subtle.deriveKey(
    {name: "PBKDF2", hash: "SHA-256", salt, iterations},
    material,
    {name: "AES-GCM", length: 256},
    false,
    usages,
  );
}

export function parseContainer(serialized) {
  let value;
  try {
    value = JSON.parse(serialized);
  } catch (error) {
    throw new Error("invalid encrypted container JSON", {cause: error});
  }
  return validateContainer(value).container;
}

export function serializeContainer(container) {
  return JSON.stringify(validateContainer(container).container);
}

export async function encryptBytes(plaintext, password, options = {}) {
  if (!(plaintext instanceof Uint8Array)) {
    throw new Error("plaintext must be a Uint8Array");
  }
  const iterations = options.iterations ?? 600_000;
  if (
    !Number.isSafeInteger(iterations)
    || iterations < 600_000
    || iterations > MAX_PBKDF2_ITERATIONS
  ) {
    throw new Error("invalid PBKDF2 iterations");
  }
  const webCrypto = requireCrypto();
  const salt = options.salt ? Uint8Array.from(options.salt) : webCrypto.getRandomValues(new Uint8Array(16));
  const iv = options.iv ? Uint8Array.from(options.iv) : webCrypto.getRandomValues(new Uint8Array(12));
  if (salt.length !== 16 || iv.length !== 12) {
    throw new Error("invalid salt or iv length");
  }
  const key = await deriveKey(password, salt, iterations, ["encrypt"]);
  const ciphertext = new Uint8Array(await webCrypto.subtle.encrypt({name: "AES-GCM", iv}, key, plaintext));
  return {
    version: 1,
    algorithm: "AES-256-GCM",
    kdf: "PBKDF2-HMAC-SHA-256",
    iterations,
    salt: bytesToBase64(salt),
    iv: bytesToBase64(iv),
    ciphertext: bytesToBase64(ciphertext),
  };
}

export async function decryptContainer(containerOrSerialized, password) {
  const container = typeof containerOrSerialized === "string"
    ? parseContainer(containerOrSerialized)
    : validateContainer(containerOrSerialized).container;
  const {salt, iv, ciphertext} = validateContainer(container);
  const key = await deriveKey(password, salt, container.iterations, ["decrypt"]);
  const plaintext = await requireCrypto().subtle.decrypt(
    {name: "AES-GCM", iv},
    key,
    ciphertext,
  );
  return new Uint8Array(plaintext);
}
