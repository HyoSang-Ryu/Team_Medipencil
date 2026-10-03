import {api,sessionSignal} from './api';
export type Job={job_id:string;status:string;error_code:string|null;result_ref:{kind:string;id:string;version?:number}|null;execution:{provider_id?:string;model?:string;execution_mode?:string;ai_executed?:boolean}};
export async function waitJob(job:Job):Promise<Job>{
 const signal=sessionSignal();
 for(let n=0;n<605&&['queued','running'].includes(job.status);n++){
  await new Promise<void>((resolve,reject)=>{
   if(signal.aborted){reject(new Error('SESSION_CHANGED'));return;}
   const abort=()=>{clearTimeout(timer);reject(new Error('SESSION_CHANGED'));};
   const timer=setTimeout(()=>{signal.removeEventListener('abort',abort);resolve();},1000);
   signal.addEventListener('abort',abort,{once:true});
  });
  if(signal.aborted)throw new Error('SESSION_CHANGED');
  job=await api<Job>(`/staff/jobs/${job.job_id}`);
 }
 if(job.status!=='succeeded'||!job.result_ref)throw new Error(job.error_code??`Job ${job.status}`);
 return job;
}
