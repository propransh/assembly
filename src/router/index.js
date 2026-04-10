import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SimulationView from '../components/debate/SimulationView.vue'
import ReportView from '../views/ReportView.vue'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', component: HomeView },
        { path: '/debate', component: SimulationView },
        { path: '/report', component: ReportView }
    ]
})

export default router