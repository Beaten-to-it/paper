import assert from "node:assert/strict";
import test from "node:test";

import {resolveProtectedArtifact} from "../site/assets/protected-viewer.js";

const artifact = {
  id: "bc2012-source",
  type: "source_paper",
  title: "Restricted source",
  status: "complete",
  access: "official_link_plus_password_encrypted",
  protected: {href: "protected/bc2012-source.enc"},
};

test("resolves only an exact catalog-declared encrypted companion", () => {
  const catalog = {papers: [{artifacts: [artifact]}]};
  assert.deepEqual(resolveProtectedArtifact(catalog, artifact.id), {
    href: "protected/bc2012-source.enc",
    title: "Restricted source",
  });
  assert.throws(() => resolveProtectedArtifact(catalog, "missing"), /available/);
});

test("rejects traversal, encoded paths, public access, and duplicate IDs", () => {
  for (const href of ["../secret.enc", "protected/../secret.enc", "protected/%2e%2e.enc", "https://example.com/a.enc"]){
    const catalog = {papers: [{artifacts: [{...artifact, protected: {href}}]}]};
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
