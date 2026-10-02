import {api} from './api';
export type Job={job_id:string;status:string;error_code:string|null;result_ref:{kind:string;id:string;version?:number}|null;execution:{provider_id?:string;model?:string;execution_mode?:string;ai_executed?:boolean}};
export async function waitJob(job:Job):Promise<Job>{
 for(let n=0;n<605&&['queued','running'].includes(job.status);n++){
  await new Promise(r=>setTimeout(r,1000));
  job=await api<Job>(`/staff/jobs/${job.job_id}`);
 }
 if(job.status!=='succeeded'||!job.result_ref)throw new Error(job.error_code??`Job ${job.status}`);
 return job;
}
