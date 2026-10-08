import aino from './assets/profile-aino.webp';
import liisa from './assets/profile-liisa.webp';
import mikko from './assets/profile-mikko.webp';
import koskinen from './assets/profile-koskinen.webp';
import {useUiLanguage} from './UiLanguage';
// Synthetic, AI-generated portraits for the PoC personas; actors without a photo keep the initial avatar.
const photos:Record<string,string>={aino,liisa,mikko,staff:koskinen};
export function Avatar({actor,name,size='md'}:{actor:string;name:string;size?:'md'|'lg'}){
 const {tr}=useUiLanguage();const photo=photos[actor];
 return photo?<img className={'account-avatar avatar-'+size} src={photo} alt={`${name} ${tr('프로필 사진')}`}/>:<span className={'account-avatar avatar-'+size} aria-hidden="true">{name.charAt(0)}</span>;
}
export function ResidentProfile(){
 const {tr}=useUiLanguage();
 return <figure className="resident-profile"><Avatar actor="aino" name="Aino" size="lg"/><figcaption><strong>Aino</strong><span>{tr('돌봄 대상자')}</span></figcaption></figure>;
}
