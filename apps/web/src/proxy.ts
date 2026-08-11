import { NextResponse, type NextRequest } from "next/server";

export function proxy(request: NextRequest) {
  const requestHeaders = new Headers(request.headers);
  const routeLocale = request.nextUrl.pathname.split("/")[1];

  if (routeLocale === "es" || routeLocale === "en") {
    requestHeaders.set("x-atlas-locale", routeLocale === "es" ? "es-MX" : "en-US");
  } else {
    requestHeaders.delete("x-atlas-locale");
  }

  return NextResponse.next({
    request: { headers: requestHeaders },
  });
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|brand|favicon.ico|robots.txt|sitemap.xml).*)"],
};
