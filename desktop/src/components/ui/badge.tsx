import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
  'inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-[var(--accent)] text-white',
        secondary: 'bg-[var(--bg-tertiary)] text-[var(--text-secondary)]',
        success: 'bg-[var(--success)] text-white',
        danger: 'bg-[var(--danger)] text-white',
        warning: 'bg-[var(--warning)] text-black',
        outline: 'border border-white/20 text-[var(--text-secondary)]',
      },
    },
    defaultVariants: { variant: 'default' },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
