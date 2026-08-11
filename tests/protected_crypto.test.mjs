import assert from "node:assert/strict";
import {execFile} from "node:child_process";
import {mkdtemp, readFile, rm, writeFile} from "node:fs/promises";
import {tmpdir} from "node:os";
import path from "node:path";
import test from "node:test";
import {promisify} from "node:util";

import {
  decryptContainer,
  encryptBytes,
  parseContainer,
  serializeContainer,
} from "../site/assets/protected-crypto.js";

const fixturePdf = new TextEncoder().encode("%PDF-1.7\nprivate fixture\n%%EOF");
const testPassword = "test-only-long-password";
const execFileAsync = promisify(execFile);
const cliPath = path.resolve("tools/protected_crypto.mjs");

test("round-trips PDF bytes with the declared cryptographic contract", async () => {
  const container = await encryptBytes(fixturePdf, testPassword);

  assert.equal(container.version, 1);
  assert.equal(container.algorithm, "AES-256-GCM");
  assert.equal(container.kdf, "PBKDF2-HMAC-SHA-256");
  assert.equal(container.iterations, 600000);
  assert.deepEqual(await decryptContainer(container, testPassword), fixturePdf);
});

test("rejects a wrong password and modified ciphertext", async () => {
  const container = await encryptBytes(fixturePdf, testPassword);

  await assert.rejects(decryptContainer(container, "wrong-password"));
  const tampered = structuredClone(container);
  const ciphertext = Buffer.from(tampered.ciphertext, "base64");
  ciphertext[0] ^= 1;
  tampered.ciphertext = ciphertext.toString("base64");
  await assert.rejects(decryptContainer(tampered, testPassword));
});

test("serialized containers expose no password, filename, or PDF bytes", async () => {
  const container = await encryptBytes(fixturePdf, testPassword);
  const serialized = serializeContainer(container);

  assert.equal(serialized.includes(testPassword), false);
  assert.equal(serialized.includes("private fixture"), false);
  assert.equal(serialized.includes("%PDF-"), false);
  assert.equal(serialized.includes(".pdf"), false);
  assert.deepEqual(parseContainer(serialized), container);
});

test("rejects malformed metadata and invalid base64 lengths", () => {
  const validShape = {
    version: 1,
    algorithm: "AES-256-GCM",
    kdf: "PBKDF2-HMAC-SHA-256",
    iterations: 600000,
    salt: "AAAAAAAAAAAAAAAAAAAAAA==",
    iv: "AAAAAAAAAAAAAAAA",
    ciphertext: "AAAAAAAAAAAAAAAAAAAAAAAA",
  };

  assert.throws(() => parseContainer(JSON.stringify({...validShape, extra: true})), /container fields/);
  assert.throws(() => parseContainer(JSON.stringify({...validShape, iterations: 599999})), /iterations/);
  assert.throws(() => parseContainer(JSON.stringify({...validShape, salt: "AAAA"})), /salt/);
  assert.throws(() => parseContainer("not json"), /JSON/);
});

test("CLI encrypts atomically from the environment and verifies the result", async () => {
  const directory = await mkdtemp(path.join(tmpdir(), "paper-protected-"));
  const source = path.join(directory, "source.pdf");
  const encrypted = path.join(directory, "artifact.enc");
  await writeFile(source, fixturePdf);
  try {
    const environment = {...process.env, PAPER_PRIVATE_PASSWORD: testPassword};
    await execFileAsync(process.execPath, [cliPath, "encrypt", "--input", source, "--output", encrypted], {env: environment});
    const serialized = await readFile(encrypted, "utf8");
    assert.deepEqual(await decryptContainer(serialized, testPassword), fixturePdf);
    await execFileAsync(process.execPath, [cliPath, "verify", "--input", encrypted, "--source", source], {env: environment});
    await assert.rejects(
      execFileAsync(process.execPath, [cliPath, "encrypt", "--input", source, "--output", encrypted], {env: environment}),
      /already exists/,
    );
  } finally {
    await rm(directory, {recursive: true, force: true});
  }
});

test("CLI refuses a missing or too-short password and non-PDF input", async () => {
  const directory = await mkdtemp(path.join(tmpdir(), "paper-protected-"));
  const source = path.join(directory, "source.pdf");
  const encrypted = path.join(directory, "artifact.enc");
  try {
    await writeFile(source, fixturePdf);
    const missing = {...process.env};
    delete missing.PAPER_PRIVATE_PASSWORD;
    await assert.rejects(
      execFileAsync(process.execPath, [cliPath, "encrypt", "--input", source, "--output", encrypted], {env: missing}),
      /PAPER_PRIVATE_PASSWORD/,
    );
    await assert.rejects(
      execFileAsync(process.execPath, [cliPath, "encrypt", "--input", source, "--output", encrypted], {
        env: {...process.env, PAPER_PRIVATE_PASSWORD: "abc"},
      }),
      /at least four/,
    );
    await writeFile(source, "not a PDF");
    await assert.rejects(
      execFileAsync(process.execPath, [cliPath, "encrypt", "--input", source, "--output", encrypted], {
        env: {...process.env, PAPER_PRIVATE_PASSWORD: testPassword},
      }),
      /PDF/,
    );
  } finally {
    await rm(directory, {recursive: true, force: true});
  }
});
