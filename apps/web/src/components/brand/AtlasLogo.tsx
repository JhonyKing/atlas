import Image from "next/image";

export type AtlasLogoVariant = "stacked" | "horizontal" | "mark";

const assets: Record<AtlasLogoVariant, { src: string; width: number; height: number }> = {
  stacked: { src: "/brand/atlas-logo-stacked.svg", width: 180, height: 140 },
  horizontal: { src: "/brand/atlas-logo-horizontal.svg", width: 148, height: 46 },
  mark: { src: "/brand/atlas-mark.svg", width: 44, height: 44 },
};

export function AtlasLogo({
  variant = "horizontal",
  alt = "ATLAS",
  className,
  priority = false,
}: {
  variant?: AtlasLogoVariant;
  alt?: string;
  className?: string;
  priority?: boolean;
}) {
  const asset = assets[variant];
  return (
    <Image
      className={className}
      src={asset.src}
      alt={alt}
      width={asset.width}
      height={asset.height}
      priority={priority}
    />
  );
}
