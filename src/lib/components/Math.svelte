<script lang="ts">
  import katex from 'katex';
  import 'katex/dist/katex.min.css';

  // กำหนด Interface สำหรับ Props ตามรูปแบบ Svelte 5
  interface MathProps {
    expression: string;     // ตัวแปรสมการ LaTeX
    displayMode?: boolean;   // true = แสดงตรงกลางบรรทัดใหม่, false = แสดงแทรกในเนื้อหา
    throwOnError?: boolean;  // ให้โยน Error ออกมาหรือไม่ถ้า Syntax ผิด
  }

  // ประกาศ Props ด้วย $props() rune
  let { 
    expression, 
    displayMode = false, 
    throwOnError = false 
  }: MathProps = $props();

  // คำนวณ String HTML ของ KaTeX แบบ Reactive ด้วย $derived.by()
  let renderedHtml = $derived.by(() => {
    try {
      return katex.renderToString(expression, {
        displayMode,
        throwOnError,
        output: 'htmlAndMathml'
      });
    } catch (error) {
      console.error('KaTeX parsing error:', error);
      // Fallback ปลอดภัยในกรณีที่สูตรคณิตศาสตร์พิมพ์มาผิดพลาด
      return `<span class="katex-error-fallback">${expression}</span>`;
    }
  });
</script>

{#if displayMode}
  <div class="svelte-math-block" role="region" aria-label="Mathematical Equation">
    {@html renderedHtml}
  </div>
{:else}
  <span class="svelte-math-inline">
    {@html renderedHtml}
  </span>
{/if}

<style>
  .svelte-math-block {
    margin: 1.5rem 0;
    overflow-x: auto;
    overflow-y: hidden;
    padding: 0.5rem;
    text-align: center;
  }

  .svelte-math-inline {
    padding: 0 0.125rem;
  }

  /* จัดการสไตล์ให้กับ Fallback Text เวลาเกิด Error */
  :global(.katex-error-fallback) {
    color: #dc2626;
    background-color: #fef2f2;
    border: 1px dashed #f87171;
    padding: 0.125rem 0.375rem;
    border-radius: 0.25rem;
    font-family: monospace;
    font-size: 0.875rem;
  }
</style>