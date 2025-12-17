# TruthTrack - Quick Start Guide

## 🚀 View the Design

### Option 1: Standalone Preview (No Backend)
1. Open `index_standalone.html` directly in your browser
2. All CSS and design elements will work
3. Verify button will show loading state but won't connect to API

### Option 2: Flask Integration (Full Functionality)
1. The main template is at `app/backend/templates/index.html`
2. Run your Flask application: `python app/backend/main.py`
3. Visit `http://localhost:5000` (or your configured port)
4. Full fact-checking functionality will be available

---

## 📁 File Locations

```
Production Files (Flask):
├── app/backend/templates/index.html     ← Main template
├── app/backend/static/css/main.css      ← All styles
├── app/backend/static/js/main.js        ← Glass interactions
└── app/backend/static/js/verification.js ← Fact-checking

Preview Files:
└── index_standalone.html                 ← Standalone demo
```

---

## 🎨 Design System Quick Reference

### Colors
```css
Primary Blue:   #1e88e5
Secondary Teal: #26c6da
Background:     #fafafa
Text:           #212121
```

### Typography
```
Headlines:  Playfair Display (Serif)
Body/UI:    Inter (Sans-serif)
```

### Glass Effect Formula
```css
backdrop-filter: blur(12px);
background: rgba(255, 255, 255, 0.7);
border: 1px solid rgba(255, 255, 255, 0.4);
box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
```

---

## ✨ Key Features

1. **Aurora Background** - Animated gradient creates depth
2. **Glassmorphic Navbar** - Sticky, blurred, elegant
3. **Floating Search Card** - Main interaction point with glow effect
4. **Feature Cards** - Hover effects with lift animation
5. **Responsive Design** - Works on mobile, tablet, desktop

---

## 🎯 Component Showcase

### Navbar
- Logo: "TruthTrack" (serif) + "AI" badge (gradient)
- Links: "Log In" text link
- Button: Gradient "Sign Up" pill button

### Hero
- Headline: "Verify the Narrative." (large serif)
- Subheadline: "Harness AI to separate fact from fiction."
- Search card with integrated verify button
- Example text: "Try: 'Climate change is a hoax'..."

### Features (3 columns)
1. Real-Time Analysis (clock icon)
2. Source Verification (document icon)
3. Bias Detection (edit icon)

### Footer
- Copyright left
- Social icons right (Twitter, LinkedIn, GitHub)

---

## 🎭 Interactive Elements

### Search Card
- **Default**: Glass effect
- **Focus**: Blue glow border
- **Typing**: Border stays blue
- **Over 500 chars**: Red border warning

### Verify Button
- **Hover**: Lifts up, shadow increases
- **Click**: Smooth press
- **Loading**: Spinning icon, disabled
- **Complete**: Returns to normal

### Feature Cards
- **Hover**: Lift animation (5px up)
- **Shadow**: Enhanced on hover

---

## 🔧 Customization Points

### Want to change colors?
Edit CSS variables in `main.css`:
```css
:root {
    --primary-blue: #YOUR_COLOR;
    --secondary-teal: #YOUR_COLOR;
}
```

### Want more/less blur?
```css
:root {
    --glass-blur: blur(16px); /* Increase number */
}
```

### Want different fonts?
Update Google Fonts import in HTML:
```html
<link href="https://fonts.googleapis.com/css2?family=YOUR_FONT&display=swap">
```

---

## 📱 Responsive Breakpoints

- **Desktop**: 1400px max-width containers
- **Tablet**: Adjusts naturally
- **Mobile**: < 768px
  - Stacked search card
  - Single column features
  - Adjusted typography sizes

---

## 🎬 Animation Reference

### Durations
- Smooth transitions: 0.3s
- Hover effects: 0.3s
- Aurora drift: 20s
- Button press: 0.15s

### Easing
- Standard: cubic-bezier(0.4, 0, 0.2, 1)
- Bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55)

---

## 🐛 Troubleshooting

### Glass effect not showing?
- Check browser support for `backdrop-filter`
- Safari needs `-webkit-backdrop-filter` prefix (already included)

### Fonts not loading?
- Check internet connection (Google Fonts CDN)
- Fonts load from: `fonts.googleapis.com`

### JavaScript not working?
- Check console for errors
- Ensure both `main.js` and `verification.js` are loaded
- Verify file paths are correct

---

## ✅ Browser Compatibility

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome  | ✅ Full | Best experience |
| Edge    | ✅ Full | Chromium-based |
| Firefox | ✅ Full | v103+ |
| Safari  | ✅ Full | v15.4+ (with prefixes) |
| Mobile  | ✅ Full | iOS Safari, Chrome |

---

## 📋 Pre-Launch Checklist

- [ ] All fonts loading properly
- [ ] Glass effects visible
- [ ] Navbar sticky on scroll
- [ ] Search card focus state working
- [ ] Button hover animations smooth
- [ ] Feature cards lift on hover
- [ ] Mobile layout looks good
- [ ] Footer links work
- [ ] Aurora background animating
- [ ] No console errors

---

## 🎯 Design Principles Applied

✅ **Journalistic Authority** - Serif headlines, clean layout  
✅ **Modern Sophistication** - Glassmorphism, subtle animations  
✅ **User-Focused** - Clear CTAs, intuitive interactions  
✅ **Performance** - Lightweight, fast load times  
✅ **Accessibility** - Semantic HTML, good contrast  
✅ **Responsive** - Works on all screen sizes  

---

## 🌟 What Makes This Special

This isn't a generic template. Every detail was crafted to convey:
- **Trust** through typography choices
- **Innovation** through glass aesthetics  
- **Clarity** through minimal design
- **Authority** through editorial layout
- **Modernity** through micro-interactions

---

## 📞 Support

For questions about the design system:
1. Check `DESIGN_DOCUMENTATION.md` for full details
2. Review CSS comments in `main.css`
3. Inspect elements in browser DevTools

---

**Status:** Production Ready ✨  
**Version:** 1.0  
**Last Updated:** December 13, 2025

Enjoy your beautiful, journalistic, ultra-modern home page! 🎉
