# Wikipedia Bot Icon

To complete the Wikipedia Bot integration, please add a Wikipedia logo image file to this directory.

## Required File
- **Filename**: `wikipedia-logo.png`
- **Location**: `static/icons/wikipedia-logo.png`

## Where to Get the Icon

### Option 1: Download from Wikipedia Commons
1. Visit: https://commons.wikimedia.org/wiki/File:Wikipedia-logo-v2.svg
2. Download the Wikipedia logo in PNG format
3. Rename it to `wikipedia-logo.png`
4. Place it in the `static/icons/` folder

### Option 2: Use a Simple Wikipedia-Themed Icon
- Search for "wikipedia icon png" on Google Images
- Download any suitable Wikipedia-themed icon (preferably 200x200px or larger)
- Save it as `wikipedia-logo.png` in the `static/icons/` folder

### Option 3: Create a Simple Placeholder
If you want to use a temporary placeholder until you get the official logo:
- Use any book or encyclopedia-themed icon
- Or create a simple icon with the letter "W"

## Alternative: Use a Text-Based Avatar
If you prefer not to use an image, you can modify the CSS to show a text-based avatar instead:

In `static/styles.css`, replace:
```css
#wikipedia-avatar {
    background-image: url('icons/wikipedia-logo.png');
}
```

With:
```css
#wikipedia-avatar {
    background: linear-gradient(135deg, #3a0647, #8b5cf6);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    font-size: 18px;
}

#wikipedia-avatar::after {
    content: 'W';
}
```

This will show a purple gradient background with a white "W" in the center.
