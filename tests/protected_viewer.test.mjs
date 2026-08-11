import assert from "node:assert/strict";
import test from "node:test";

import {encryptBytes, serializeContainer} from "../site/assets/protected-crypto.js";
import {
  resolveProtectedArtifact,
  verifyEncryptedPayload,
} from "../site/assets/protected-viewer.js";

const artifact = {
  id: "bc2012-source",
  type: "source_paper",
  title: "Restricted source",
  status: "complete",
  access: "official_link_plus_password_encrypted",
  protected: {
    href: "protected/bc2012-source.enc",
    size_bytes: 123,
    sha256: "a".repeat(64),
    container_version: 1,
    algorithm: "AES-256-GCM",
    kdf: "PBKDF2-HMAC-SHA-256",
    iterations: 600000,
  },
};

test("resolves only an exact catalog-declared encrypted companion", () => {
  const catalog = {papers: [{artifacts: [artifact]}]};
  assert.deepEqual(resolveProtectedArtifact(catalog, artifact.id), {
    href: "protected/bc2012-source.enc",
    title: "Restricted source",
    expected: artifact.protected,
  });
  assert.throws(() => resolveProtectedArtifact(catalog, "missing"), /available/);
});

test("rejects traversal, encoded paths, public access, and duplicate IDs", () => {
  for (const href of ["../secret.enc", "protected/../secret.enc", "protected/%2e%2e.enc", "https://example.com/a.enc"]){
    const catalog = {papers: [{artifacts: [{...artifact, protected: {...artifact.protected, href}}]}]};
    assert.throws(() => resolveProtectedArtifact(catalog, artifact.id), /path/);
  }
  assert.throws(
    () => resolveProtectedArtifact({papers: [{artifacts: [{...artifact, access: "public"}]}]}, artifact.id),
    /access/,
  );
  assert.throws(
    () => resolveProtectedArtifact({papers: [{artifacts: [artifact]}, {artifacts: [artifact]}]}, artifact.id),
    /available/,
  );
});

async function sha256Hex(bytes) {
  const digest = new Uint8Array(await crypto.subtle.digest("SHA-256", bytes));
  return [...digest].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

test("binds the served ciphertext to the catalog size, hash, and crypto metadata", async () => {
  const password = "test-only-long-password";
  const expectedSerialized = serializeContainer(await encryptBytes(new TextEncoder().encode("%PDF-1.7\nEXPECTED-A"), password));
  const substitutedSerialized = serializeContainer(await encryptBytes(new TextEncoder().encode("%PDF-1.7\nREPLACED-B"), password));
  const expectedBytes = new TextEncoder().encode(expectedSerialized);
  const substitutedBytes = new TextEncoder().encode(substitutedSerialized);
  const metadata = {
    ...artifact.protected,
    size_bytes: expectedBytes.length,
    sha256: await sha256Hex(expectedBytes),
  };

  const container = await verifyEncryptedPayload(expectedBytes, metadata);
  assert.equal(container.iterations, metadata.iterations);
  await assert.rejects(verifyEncryptedPayload(substitutedBytes, metadata), /integrity/);
  await assert.rejects(
    verifyEncryptedPayload(expectedBytes, {...metadata, size_bytes: metadata.size_bytes + 1}),
    /size/,
  );
  await assert.rejects(
    verifyEncryptedPayload(expectedBytes, {...metadata, iterations: metadata.iterations + 1}),
    /metadata/,
  );
});
