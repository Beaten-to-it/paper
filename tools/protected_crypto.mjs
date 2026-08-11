import {createHash, timingSafeEqual, randomUUID} from "node:crypto";
import {link, mkdir, readFile, rm, writeFile} from "node:fs/promises";
import path from "node:path";

import {
  decryptContainer,
  encryptBytes,
  parseContainer,
  serializeContainer,
} from "../site/assets/protected-crypto.js";

function usage() {
  return "usage: protected_crypto.mjs encrypt --input <pdf> --output <enc> | verify --input <enc> --source <pdf>";
}

function parseArguments(argv) {
  const [command, ...tokens] = argv;
  if (!new Set(["encrypt", "verify"]).has(command) || tokens.length % 2 !== 0) {
    throw new Error(usage());
  }
  const options = {};
  for (let index = 0; index < tokens.length; index += 2) {
    const name = tokens[index];
    const value = tokens[index + 1];
    if (!name?.startsWith("--") || !value || options[name]) {
      throw new Error(usage());
    }
    options[name] = value;
  }
  const expected = command === "encrypt" ? ["--input", "--output"] : ["--input", "--source"];
  if (Object.keys(options).length !== expected.length || expected.some((name) => !options[name])) {
    throw new Error(usage());
  }
  return {command, options};
}

function requirePassword() {
  const password = process.env.PAPER_PRIVATE_PASSWORD;
  if (typeof password !== "string" || password.length < 4) {
    throw new Error("PAPER_PRIVATE_PASSWORD must contain at least four characters");
  }
  return password;
}

function requirePdf(bytes) {
  if (bytes.length < 5 || bytes.subarray(0, 5).toString("ascii") !== "%PDF-") {
    throw new Error("input is not a PDF file");
  }
}

function sameDigest(left, right) {
  const leftHash = createHash("sha256").update(left).digest();
  const rightHash = createHash("sha256").update(right).digest();
  return timingSafeEqual(leftHash, rightHash);
}

async function encryptFile(inputName, outputName, password) {
  const input = path.resolve(inputName);
  const output = path.resolve(outputName);
  if (input === output || path.extname(output).toLowerCase() !== ".enc") {
    throw new Error("output must be a distinct .enc file");
  }
  const plaintext = await readFile(input);
  requirePdf(plaintext);
  const serialized = serializeContainer(await encryptBytes(plaintext, password));
  const temporary = path.join(path.dirname(output), `.${path.basename(output)}.${process.pid}.${randomUUID()}.tmp`);
  await mkdir(path.dirname(output), {recursive: true});
  try {
    await writeFile(temporary, serialized, {encoding: "utf8", flag: "wx", mode: 0o600});
    const written = await readFile(temporary, "utf8");
    const decrypted = await decryptContainer(parseContainer(written), password);
    if (!sameDigest(plaintext, decrypted)) {
      throw new Error("encrypted file verification failed");
    }
    try {
      await link(temporary, output);
    } catch (error) {
      if (error?.code === "EEXIST") {
        throw new Error("output already exists");
      }
      throw error;
    }
  } finally {
    await rm(temporary, {force: true});
  }
  process.stdout.write("encrypted and verified\n");
}

async function verifyFile(inputName, sourceName, password) {
  const encrypted = await readFile(path.resolve(inputName), "utf8");
  const source = await readFile(path.resolve(sourceName));
  requirePdf(source);
  const decrypted = await decryptContainer(parseContainer(encrypted), password);
  requirePdf(Buffer.from(decrypted));
  if (!sameDigest(source, decrypted)) {
    throw new Error("decrypted content does not match source PDF");
  }
  process.stdout.write("verified\n");
}

async function main() {
  const {command, options} = parseArguments(process.argv.slice(2));
  const password = requirePassword();
  if (command === "encrypt") {
    await encryptFile(options["--input"], options["--output"], password);
  } else {
    await verifyFile(options["--input"], options["--source"], password);
  }
}

main().catch((error) => {
  process.stderr.write(`${error instanceof Error ? error.message : "operation failed"}\n`);
  process.exitCode = 1;
});
