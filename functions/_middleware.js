// Cloudflare Pages does not honour .assetsignore by itself, so the source tree
// (data/, tools/, README, build scripts) would otherwise be downloadable.
// This middleware keeps every non-public path at 404 while the static site is served as usual.
const BLOCK_PREFIXES = ['/data/', '/tools/', '/functions/', '/.github/', '/.git/'];
const BLOCK_EXACT = new Set([
  '/data', '/tools', '/functions', '/README.md', '/.assetsignore', '/.gitignore', '/.stories_extract.json',
]);

export async function onRequest(context) {
  const { pathname } = new URL(context.request.url);
  const blocked =
    BLOCK_PREFIXES.some((p) => pathname.startsWith(p)) ||
    BLOCK_EXACT.has(pathname) ||
    /\.(py|pyc|md)$/i.test(pathname);

  if (blocked) {
    return new Response('Not Found', {
      status: 404,
      headers: { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store' },
    });
  }
  return context.next();
}
