import { defineConfig } from 'vitepress'

const SITE_URL = 'https://log.fieldnotes.jp'

function ogImageUrl(relativePath: string): string {
  if (relativePath.startsWith('slides/') && relativePath !== 'slides/index.md') {
    const slug = relativePath.replace(/^slides\//, '').replace(/\.md$/, '')
    return `${SITE_URL}/ogp/slides/${slug}.png`
  }
  const slug = relativePath.replace(/\.md$/, '').replace(/\//g, '__')
  if (!slug || slug === 'index') return `${SITE_URL}/ogp/default.png`
  return `${SITE_URL}/ogp/${slug}.png`
}

export default defineConfig({
  lang: 'ja',
  title: 'log.fieldnotes.jp',
  description: 'log.fieldnotes.jp',

  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    ['script', { async: '', src: 'https://www.googletagmanager.com/gtag/js?id=G-YELXGEQW4R' }],
    ['script', {}, `window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-YELXGEQW4R');`],
  ],

  sitemap: {
    hostname: SITE_URL,
  },

  transformHead({ pageData, siteData }) {
    const fm = pageData.frontmatter
    const pageTitle = fm.title
      ? `${fm.title} | ${siteData.title}`
      : siteData.title
    const description = fm.description || siteData.description
    const pageUrl = `${SITE_URL}/${pageData.relativePath.replace(/\.md$/, '.html').replace(/index\.html$/, '')}`
    const ogImage = ogImageUrl(pageData.relativePath)

    return [
      ['meta', { property: 'og:type',        content: 'website' }],
      ['meta', { property: 'og:site_name',   content: siteData.title }],
      ['meta', { property: 'og:title',       content: pageTitle }],
      ['meta', { property: 'og:description', content: description }],
      ['meta', { property: 'og:url',         content: pageUrl }],
      ['meta', { property: 'og:image',       content: ogImage }],
      ['meta', { name: 'twitter:card',        content: 'summary_large_image' }],
      ['meta', { name: 'twitter:site',        content: '@setoazusa' }],
      ['meta', { name: 'twitter:title',       content: pageTitle }],
      ['meta', { name: 'twitter:description', content: description }],
      ['meta', { name: 'twitter:image',       content: ogImage }],
    ]
  },

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
      copyright: '© 2026 Hiroyuki Ohnaka',
    },
  },
})
