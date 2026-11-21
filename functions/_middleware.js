// 21.11.2026: the old address markoboskotherapies.pages.dev forwards to therapies.markobosko.org (301, path and query kept).
// Only the exact production host: preview hosts hash.markoboskotherapies.pages.dev are never redirected.
// GET and HEAD only, so form POSTs keep working. Once the account Bulk Redirect list pagesdev_to_markobosko_org
// is on (~/Developer/claude-code/tools/pagesdev_redirects.py) this file is redundant but harmless.
const OLD = new Set(['markoboskotherapies.pages.dev']);
export async function onRequest(ctx) {
  const u = new URL(ctx.request.url);
  const m = ctx.request.method;
  if (OLD.has(u.hostname) && (m === 'GET' || m === 'HEAD')) {
    return Response.redirect('https://therapies.markobosko.org' + u.pathname + u.search, 301);
  }
  return ctx.next();
}
