export const API=(import.meta.env.VITE_API_URL||"http://localhost:8000/api").replace(/\/$/,"");
export type Hall={id:number;name:string;slug:string;description:string;image_url:string;capacity:number;base_price:string};
export type Package={id:number;name:string;description:string;price:string};
export type Menu={id:number;name:string;category:string;price_per_guest:string};
export type Booking={id:number;hall:number;hall_name:string;package:number;package_name:string;date:string;guests:number;name:string;phone:string;total:string;status:string};
export const readToken=()=>sessionStorage.getItem("royal_token");
export async function request<T>(path:string,options:RequestInit={}):Promise<T>{
 const headers:Record<string,string>={"Content-Type":"application/json",...(options.headers as Record<string,string>||{})};
 const token=readToken(); if(token) headers.Authorization="Token "+token;
 const response=await fetch(API+path,{...options,headers});
 const data=await response.json().catch(()=>null);
 if(!response.ok) throw new Error(typeof data?.detail==="string"?data.detail:JSON.stringify(data||"Request failed"));
 return data as T;
}
