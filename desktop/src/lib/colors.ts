export function roleColorToHex(color: number): string {
  return `#${Math.max(0, Math.min(0xFFFFFF, color)).toString(16).padStart(6, '0')}`;
}
