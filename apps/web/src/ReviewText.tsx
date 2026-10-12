import {useUiLanguage} from './UiLanguage';
import {koreanReviewTranslation} from './reviewTranslation';
export function ReviewText({text}:{text:string}){
 const {language}=useUiLanguage();
 if(language!=='ko')return <>{text}</>;
 const translated=koreanReviewTranslation(text);
 if(!translated)return <>{text}<small className="review-translation-note">한국어 검토문 미제공 · 원문을 확인하세요.</small></>;
 return <span className="review-bilingual"><span className="review-korean">{translated}</span><small className="review-translation-note">한국어 검토용 설명 · 합성 예문 번역, AI 번역 아님</small><span className="review-original" lang="fi"><small>원문</small> {text}</span></span>;
}
