import { defineConfig } from 'vitepress'

export default defineConfig({
  lang: 'ja',
  title: 'log.fieldnotes.jp',
  description: 'hiroyuki ohnaka\'s portfolio',

  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
  ],

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Blog', link: '/blog/' },
      { text: 'Slides', link: '/slides/' },
    ],

    socialLinks: [
      { icon: 'x', link: 'https://x.com/setoazusa' },
      { icon: 'instagram', link: 'https://www.instagram.com/hiroyuki_7171/' },
      { icon: 'github', link: 'https://github.com/azusa/' },
    ],

    footer: {
      copyright: '© 2026 hiroyuki ohnaka',
    },
  },
})
