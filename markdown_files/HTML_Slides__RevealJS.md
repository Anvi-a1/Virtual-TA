---
title: "HTML Slides: RevealJS"
original_url: "https://tds.s-anand.net/#/revealjs?id=configuration"
downloaded_at: "2025-11-17T02:04:04.787404"
---
[RevealJS: Web-Based Presentations](#/revealjs?id=revealjs-web-based-presentations)
-----------------------------------------------------------------------------------

[![Create Beautiful HTML Presentations with RevealJS (25 min)](https://i.ytimg.com/vi/a6ioNtv2H-E/sddefault.jpg)](https://www.youtube.com/watch?v=a6ioNtv2H-E&list=PLoqZcxvpWzzf_C8QgHC9XbA-bn18qJ-QV)

[RevealJS](https://revealjs.com/) is a powerful HTML presentation framework that turns web pages into interactive slideshows. It’s particularly useful for:

* **Data Presentations**: Interactive charts, live data demos
* **Technical Talks**: Code with syntax highlighting, math equations
* **Web Portfolios**: Showcase projects with live demos
* **Educational Content**: Interactive learning materials
* **Conference Talks**: Remote-friendly with speaker notes
* **Documentation**: API and library showcases

This tutorial covers creating interactive presentations with RevealJS.

### [Installation](#/revealjs?id=installation)

Multiple ways to get started:

```
# Using npm (recommended for customization)
npm install reveal.js

# Quick start with CDN (add to HTML)
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/theme/white.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.js"></script>

# Start a new presentation (creates template)
npx create-reveal-app my-presentationCopy to clipboardErrorCopied
```

### [Basic Structure](#/revealjs?id=basic-structure)

A minimal RevealJS presentation:

```
<!DOCTYPE html>
<html>
  <head>
    <link rel="stylesheet" href="dist/reveal.css" />
    <link rel="stylesheet" href="dist/theme/white.css" />
  </head>
  <body>
    <div class="reveal">
      <div class="slides">
        <section>Slide 1</section>
        <section>Slide 2</section>
      </div>
    </div>
    <script src="dist/reveal.js"></script>
    <script>
      Reveal.initialize();
    </script>
  </body>
</html>Copy to clipboardErrorCopied
```

### [Markdown Support](#/revealjs?id=markdown-support)

RevealJS can use Markdown for content:

```
<section data-markdown>
  <textarea data-template>
    ## Slide Title

    - Bullet point 1
    - Bullet point 2

    ---

    ## Next Slide

    ```python
    def hello():
        print("Hello, World!")
    ```
  </textarea>
</section>Copy to clipboardErrorCopied
```

### [Interactive Elements](#/revealjs?id=interactive-elements)

RevealJS shines with interactive content:

```
<!-- Interactive Chart with D3 -->
<section>
  <h2>Live Data Visualization</h2>
  <div class="chart" id="d3-chart"></div>
  <script>
    d3.select("#d3-chart").append("svg");
    // ... D3 visualization code
  </script>
</section>

<!-- iframe for Live Demo -->
<section>
  <h2>Live Demo</h2>
  <iframe data-src="https://example.com/demo" data-preload></iframe>
</section>Copy to clipboardErrorCopied
```

### [Fragments and Animations](#/revealjs?id=fragments-and-animations)

Reveal content gradually:

```
<!-- List items appear one by one -->
<section>
  <h2>Key Points</h2>
  <ul>
    <li class="fragment">First point</li>
    <li class="fragment">Second point</li>
    <li class="fragment fade-up">Animated point</li>
  </ul>
</section>

<!-- Chart sections appear gradually -->
<section>
  <h2>Data Flow</h2>
  <div class="r-stack">
    <img class="fragment" src="step1.svg" />
    <img class="fragment" src="step2.svg" />
    <img class="fragment" src="step3.svg" />
  </div>
</section>Copy to clipboardErrorCopied
```

### [Code Presentation](#/revealjs?id=code-presentation)

Code with syntax highlighting and animations:

```
<section>
  <pre><code class="python" data-line-numbers="1-2|4,6-7|9">
import pandas as pd
import seaborn as sns

# Load data
data = pd.read_csv('data.csv')

# Create visualization
sns.scatterplot(data=data, x='x', y='y')
  </code></pre>
</section>Copy to clipboardErrorCopied
```

### [Math and Diagrams](#/revealjs?id=math-and-diagrams)

Support for equations and diagrams:

```
<!-- Math equations using MathJax -->
<section>
  <h2>Statistical Formula</h2>
  \[P(A|B) = \frac{P(B|A)P(A)}{P(B)}\]
</section>

<!-- Mermaid diagrams -->
<section>
  <div class="mermaid">graph TD A[Data] -->|Process| B[Analysis] B --> C[Visualization]</div>
</section>Copy to clipboardErrorCopied
```

### [Themes and Styling](#/revealjs?id=themes-and-styling)

Custom styling with CSS:

```
/* Custom theme */
.reveal {
  font-family: "Arial", sans-serif;
}

/* Custom classes */
.reveal .slides section.has-dark-background {
  color: #fff;
}

/* Chart-specific styling */
.chart {
  height: 400px;
  margin: 20px auto;
}Copy to clipboardErrorCopied
```

### [Configuration](#/revealjs?id=configuration)

Common configuration options:

```
Reveal.initialize({
  // Display
  width: 1280,
  height: 720,
  margin: 0.04,

  // Navigation
  controls: true,
  progress: true,
  history: true,

  // Presentation Features
  autoSlide: 0,
  transition: "slide",

  // Plugins
  plugins: [RevealMarkdown, RevealHighlight, RevealMath, RevealNotes],
});Copy to clipboardErrorCopied
```

### [Presentation Modes](#/revealjs?id=presentation-modes)

Special presentation features:

```
// Speaker notes
<section>
  <h2>Slide Title</h2>
  <p>Visible content</p>
  <aside class="notes">Speaker notes visible in presenter view</aside>
</section>;

// Overview mode (press 'o')
Reveal.addEventListener("overviewshown", function () {
  // Custom overview behavior
});Copy to clipboardErrorCopied
```

### [Data Visualization Integration](#/revealjs?id=data-visualization-integration)

RevealJS works well with visualization libraries:

```
<!-- D3.js Integration -->
<section>
  <div id="chart"></div>
  <script>
    const data = [
      /* ... */
    ];

    Reveal.addEventListener("slidechanged", function (event) {
      if (event.currentSlide.id === "chart-slide") {
        updateChart(data);
      }
    });
  </script>
</section>

<!-- Observable Plot -->
<section>
  <div id="plot"></div>
  <script type="module">
    import * as Plot from "https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6/+esm";
    // Create interactive plot
  </script>
</section>Copy to clipboardErrorCopied
```

### [Best Practices](#/revealjs?id=best-practices)

1. **Project Structure**:

   ```
   presentation/
   ├── index.html
   ├── css/
   │   └── custom.css
   ├── js/
   │   └── visualizations.js
   ├── data/
   │   └── analysis.json
   └── images/
       └── diagrams/Copy to clipboardErrorCopied
   ```
2. **Performance Tips**:

   * Lazy load images and iframes
   * Preload critical slides
   * Optimize data visualizations
   * Use appropriate image formats
3. **Responsive Design**:

   ```
   /* Responsive font sizes */
   :root {
     --r-main-font-size: calc(0.5vw + 0.5vh + 0.5vmin);
   }

   /* Responsive charts */
   .chart {
     width: 100%;
     height: calc(100vh - 200px);
   }Copy to clipboardErrorCopied
   ```
4. **Deployment**:

   ```
   # Build for production
   npm run build

   # Deploy to GitHub Pages
   npm run deployCopy to clipboardErrorCopied
   ```

### [Common Issues](#/revealjs?id=common-issues)

1. **Visualization Scaling**

   * Use responsive SVG viewBox
   * Scale based on container size
   * Test on different screen sizes
2. **Plugin Loading**

   * Load plugins before initialization
   * Check console for loading errors
   * Use async loading when needed
3. **Print/PDF Export**

   ```
   # Using decktape for PDF export
   npx decktape reveal http://localhost:8000 slides.pdfCopy to clipboardErrorCopied
   ```

### [Keyboard Shortcuts](#/revealjs?id=keyboard-shortcuts)

Essential shortcuts for presenting:

* `F` - Fullscreen
* `S` - Speaker notes
* `O` - Overview
* `B` - Pause (black screen)
* `.` - Pause (blank screen)
* `ESC` - Overview mode
* `?` - Show help

[Previous

Data Storytelling](#/data-storytelling)

[Next

Markdown Presentations: Marp](#/marp)