<script lang="ts">
  import Prism from 'prismjs';
  // นำเข้า Theme สำเร็จรูปของ Prism
  import 'prismjs/themes/prism-tomorrow.css';

  interface CodeProps {
    code: string;           // ซอร์สโค้ดดิบ
    language?: string;      // ภาษาคอมพิวเตอร์ เช่น 'javascript', 'typescript', 'python'
    filename?: string;      // ชื่อไฟล์ (ถ้ามี)
  }

  let { 
    code, 
    language = 'javascript', 
    filename = '' 
  }: CodeProps = $props();

  // ฟังก์ชันทำความสะอาดและแปลงโค้ดให้ออกมาเป็นโครงสร้าง HTML ไฮไลต์สี
  let highlightedCode = $derived.by(() => {
    const cleanCode = code.trim();
    const grammar = Prism.languages[language];

    if (grammar) {
      return Prism.highlight(cleanCode, grammar, language);
    }

    // หากไม่พบภาษาที่ระบุ ให้ทำการแปลง HTML Entity เพื่อความปลอดภัย (XSS Prevention)
    return cleanCode
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  });
</script>

<div class="svelte-code-wrapper">
  {#if filename}
    <div class="code-header">
      <span class="filename-text">{filename}</span>
      <span class="language-badge">{language}</span>
    </div>
  {:else}
    <div class="code-header-minimal">
      <span class="language-badge">{language}</span>
    </div>
  {/if}

  <pre class="language-{language}"><code class="language-{language}">{@html highlightedCode}</code></pre>
</div>

<style>
  .svelte-code-wrapper {
    display: flex;
    flex-direction: column;
    border-radius: 0.5rem;
    overflow: hidden;
    margin: 1.5rem 0;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    background-color: #2d2d2d;
  }

  .code-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #1e1e1e;
    padding: 0.5rem 1rem;
    border-bottom: 1px solid #3e3e3e;
  }

  .code-header-minimal {
    display: flex;
    justify-content: flex-end;
    background-color: transparent;
    position: absolute;
    right: 1rem;
    margin-top: 0.5rem;
    z-index: 10;
  }

  .filename-text {
    color: #9ca3af;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    font-size: 0.8125rem;
  }

  .language-badge {
    color: #6b7280;
    background-color: #374151;
    padding: 0.125rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    text-transform: uppercase;
    font-weight: 600;
  }

  pre {
    margin: 0 !important;
    padding: 1.25rem !important;
    overflow-x: auto;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
    font-size: 0.9rem !important;
    line-height: 1.5 !important;
    background: transparent !important;
  }

  code {
    font-family: inherit !important;
    background: transparent !important;
    padding: 0 !important;
  }
</style>