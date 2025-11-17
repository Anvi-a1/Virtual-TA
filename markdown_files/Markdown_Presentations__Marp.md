---
title: "Markdown Presentations: Marp"
original_url: "https://tds.s-anand.net/#/marp?id=themes"
downloaded_at: "2025-11-17T01:52:51.293784"
---
[Marp: Markdown Presentation Ecosystem](#/marp?id=marp-markdown-presentation-ecosystem)
---------------------------------------------------------------------------------------

[![Never use PowerPoint again (20 min)](https://i.ytimg.com/vi/EzQ-p41wNEE/sddefault.jpg)](https://youtu.be/EzQ-p41wNEE)

[Marp](https://marp.app/) (Markdown Presentation) is a powerful tool for creating presentations using Markdown. It converts Markdown files into slideshows, making it ideal for:

* **Technical Presentations**: Code snippets, diagrams, and technical content
* **Documentation**: Creating slide decks from existing documentation
* **Academic Slides**: Research presentations with math equations and citations
* **Conference Talks**: Professional presentations with custom themes
* **Teaching Materials**: Educational content with rich formatting
* **GitHub Pages**: Hosting presentations on the web

This tutorial covers using Marp in VS Code to create professional presentations.

### [Installation](#/marp?id=installation)

Install the Marp extension and CLI for different ways to preview and export:

```
# Install Marp CLI globally
npm install -g @marp-team/marp-cli

# For one-time use without installing
npx @marp-team/marp-cli@latest

# For use in a project
npm install --save-dev @marp-team/marp-cliCopy to clipboardErrorCopied
```

### [Basic Structure](#/marp?id=basic-structure)

Every Marp presentation starts with YAML front matter and uses `---` to separate slides:

```
---
marp: true
title: My Presentation
author: Your Name
theme: default
paginate: true
---

# First Slide

Content goes here

---

## Second Slide

More contentCopy to clipboardErrorCopied
```

### [Themes](#/marp?id=themes)

Marp comes with built-in themes and supports custom themes:

```
---
theme: default    # Clean, minimal (default)
theme: gaia      # Modern, beautiful
theme: uncover   # Gradually revealing
---Copy to clipboardErrorCopied
```

Create custom themes with CSS:

```
---
marp: true
---

<style>
section {
  background: #fdf6e3;
  color: #657b83;
}
h1 {
  color: #d33682;
}
</style>Copy to clipboardErrorCopied
```

### [Images and Backgrounds](#/marp?id=images-and-backgrounds)

Marp has powerful image handling:

```
![](image.jpg) # Regular image
![width:500px](image.jpg) # Set width
![height:300px](image.jpg) # Set height
![w:500 h:300](image.jpg) # Both width & height

<!-- Background image -->

![bg](background.jpg)
![bg fit](background.jpg) # Fit to slide
![bg cover](background.jpg) # Cover slide

<!-- Multiple backgrounds -->

![bg left](left.jpg)
![bg right](right.jpg)Copy to clipboardErrorCopied
```

### [Directives](#/marp?id=directives)

Control presentation flow with directives:

```
<!-- _class: lead -->

# Title Slide

<!-- _backgroundColor: #123456 -->

Slide with custom background

<!-- _color: red -->

Red text

<!-- _footer: *Page footer* -->

Content with footer

<!-- _header: **Header** -->

Content with headerCopy to clipboardErrorCopied
```

### [Code Blocks](#/marp?id=code-blocks)

Code highlighting with language specification:

```
```python
def hello():
    print("Hello, World!")
```

```javascript
console.log("Hello, World!");
```

```css
body {
  background: #fff;
}
```Copy to clipboardErrorCopied
```

### [Math Equations](#/marp?id=math-equations)

Marp supports math with KaTeX:

```
Inline math: $E = mc^2$

Block math:

$$
\frac{d}{dx}e^x = e^x
$$Copy to clipboardErrorCopied
```

### [Tables and Lists](#/marp?id=tables-and-lists)

Standard Markdown tables and lists work:

```
| Item | Cost |
| ---- | ---- |
| A    | $1   |
| B    | $2   |

- Bullet point
  - Sub-point
    - Sub-sub-point

1. Numbered list
2. Second item
   - Mixed listCopy to clipboardErrorCopied
```

### [Building & Exporting](#/marp?id=building-amp-exporting)

Export to various formats:

```
# HTML (for web)
marp slides.md -o slides.html

# PDF (for sharing)
marp slides.md --pdf

# PowerPoint
marp slides.md --pptx

# Images (PNG/JPEG)
marp slides.md --images pngCopy to clipboardErrorCopied
```

With VS Code integration:

```
---
marp: true
---

<!-- In VS Code, use Command Palette:
     - "Marp: Export Slide Deck..."
     - "Marp: Start Watch"
     - "Marp: Toggle Preview"
-->Copy to clipboardErrorCopied
```

### [Real Example: Data Design by Dialogue](#/marp?id=real-example-data-design-by-dialogue)

Here’s a [real presentation example](https://github.com/sanand0/talks/tree/main/2025-06-27-data-design-by-dialogue) and [slide output](https://sanand0.github.io/talks/2025-06-27-data-design-by-dialogue/) that shows these features in action:

```
---
marp: true
title: Data Design by Dialogue
author: Anand S
theme: gaia
paginate: true
---

<style>
  blockquote {
    font-style: italic;
  }
  section {
    background-image: url('qr-code.png');
    background-repeat: no-repeat;
    background-position: top 20px right 20px;
    background-size: 80px auto;
  }
</style>

# Data Design by Dialogue

Content with styled quotes and background image...Copy to clipboardErrorCopied
```

### [Best Practices](#/marp?id=best-practices)

1. **File Organization**:

   ```
   presentation/
   ├── slides.md        # Main presentation
   ├── images/          # Images folder
   ├── themes/          # Custom themes
   └── package.json     # Build configurationCopy to clipboardErrorCopied
   ```
2. **Version Control**:

   ```
   .gitignore:
   node_modules/
   dist/
   *.pdf
   *.pptxCopy to clipboardErrorCopied
   ```
3. **Build Automation**:

   ```
   {
     "scripts": {
       "start": "marp -s .",
       "build": "marp slides.md -o dist/slides.html",
       "pdf": "marp slides.md --pdf --allow-local-files",
       "pptx": "marp slides.md --pptx"
     }
   }Copy to clipboardErrorCopied
   ```
4. **Responsive Design**:

   ```
   /* themes/custom.css */
   section {
     font-size: calc(1.2vw + 1.2vh);
   }Copy to clipboardErrorCopied
   ```

Remember to:

* Keep slides focused and minimal
* Use consistent styling
* Test the presentation in the target format
* Include speaker notes when needed
* Optimize images before including

### [Common Issues](#/marp?id=common-issues)

1. **Images Not Loading**

   * Use relative paths from the Markdown file
   * Add `--allow-local-files` for local images in PDF export
2. **Font Problems**

   * Include web fonts in your custom theme
   * Test PDF export with custom fonts
3. **Build Errors**

   * Check Node.js version compatibility
   * Verify all dependencies are installed
   * Use `--verbose` flag for debugging

### [Keyboard Shortcuts](#/marp?id=keyboard-shortcuts)

In VS Code Marp Preview:

* `F1` then “Marp: Toggle Preview”
* `Ctrl+Shift+V` (Preview)
* `Ctrl+K V` (Side Preview)

In Presentation Mode:

* `F` (Fullscreen)
* `P` (Presenter View)
* `B` (Blackout)

[Previous

HTML Slides: RevealJS](#/revealjs)

[Next

Interactive Notebooks: Marimo](#/marimo)