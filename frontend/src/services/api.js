import axios from 'axios';
const client=axios.create({baseURL:import.meta.env.VITE_API_URL||'http://localhost:8000'});
export const api={couplings:()=>client.get('/couplings').then(r=>r.data),coupling:id=>client.get(`/couplings/${id}`).then(r=>r.data),recommend:data=>client.post('/recommend',data).then(r=>r.data),compare:coupling_ids=>client.post('/compare',{coupling_ids}).then(r=>r.data),calculateTorque:(power,power_unit,speed)=>client.post('/calculate-torque',{power,power_unit,speed}).then(r=>r.data)};
