import { createApp } from "vue"
import App from "./App.vue"
import { router } from "./router"
import { createPinia } from "pinia"

import Toast from "vue-toastification"
import "vue-toastification/dist/index.css"

import "./assets/styles.css"

const app = createApp(App)

app.use(router)
app.use(createPinia())
app.use(Toast, {
  position: "top-right",
  timeout: 4000,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
  showCloseButtonOnHover: true,
  hideProgressBar: false,
})

app.mount("#app")