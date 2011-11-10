// ==UserScript==
// @name YouTube Force HTML5 Fullscreen
// @description YouTube Fullscreen
// @include http://*.youtube.com/watch?*
// @include https://*.youtube.com/watch?*
// @match http://*.youtube.com/watch?*
// @match https://*.youtube.com/watch?*
// ==/UserScript==

// Switch to fullscreen on page load
document.body.className += ' html5-fullscreen';

// Hide annotations
document.querySelector('.video-annotations').style.display = 'none';

// Change progress bar red to a light grey; less distractions
document.querySelector('.html5-play-progress.html5-progress-section').style.background = '#222222';
