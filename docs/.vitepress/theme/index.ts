import DefaultTheme from 'vitepress/theme'

import './custom.css'
import ConversationLayout from './ConversationLayout.vue'

export default {
  extends: DefaultTheme,
  Layout: ConversationLayout,
}
