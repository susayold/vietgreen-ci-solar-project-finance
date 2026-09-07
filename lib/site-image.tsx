import Image from 'next/image';
import type { ComponentProps } from 'react';
export default function SiteImage(props: ComponentProps<typeof Image>) {
  const prefix = process.env.NEXT_PUBLIC_SITE_BASE_PATH || '';
  const src = typeof props.src === 'string' && props.src.startsWith('/assets/') ? prefix + props.src : props.src;
  return <Image {...props} src={src} />;
}
