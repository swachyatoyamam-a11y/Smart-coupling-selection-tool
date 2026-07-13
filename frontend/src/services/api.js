import axios from 'axios';
const client=axios.create({baseURL:import.meta.env.VITE_API_URL||'http://localhost:8000'});
export const api={couplings:()=>client.get('/couplings').then(r=>r.data),recommend:data=>client.post('/recommend',data).then(r=>r.data),compare:data=>client.post('/compare',data).then(r=>r.data),calculateTorque:(power,speed)=>client.post('/calculate-torque',{power,speed}).then(r=>r.data)};
