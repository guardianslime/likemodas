import{F as e,I as t}from"./chunk-C37GKA54-CfNxjTQL.js";var n={styles:{global:{":root":{},body:{fontFamily:`Arial, sans-serif`,"--default-font-family":`Arial, sans-serif`}}}};
/**
* @license lucide-react v0.534.0 - ISC
*
* This source code is licensed under the ISC license.
* See the LICENSE file in the root directory of this source tree.
*/
const r=e=>e.replace(/([a-z0-9])([A-Z])/g,`$1-$2`).toLowerCase(),i=e=>e.replace(/^([A-Z])|[\s-_]+(\w)/g,(e,t,n)=>n?n.toUpperCase():t.toLowerCase()),a=e=>{let t=i(e);return t.charAt(0).toUpperCase()+t.slice(1)},o=(...e)=>e.filter((e,t,n)=>!!e&&e.trim()!==``&&n.indexOf(e)===t).join(` `).trim(),s=e=>{for(let t in e)if(t.startsWith(`aria-`)||t===`role`||t===`title`)return!0};
/**
* @license lucide-react v0.534.0 - ISC
*
* This source code is licensed under the ISC license.
* See the LICENSE file in the root directory of this source tree.
*/
var c={xmlns:`http://www.w3.org/2000/svg`,width:24,height:24,viewBox:`0 0 24 24`,fill:`none`,stroke:`currentColor`,strokeWidth:2,strokeLinecap:`round`,strokeLinejoin:`round`},l=t(e());const u=(0,l.forwardRef)(({color:e=`currentColor`,size:t=24,strokeWidth:n=2,absoluteStrokeWidth:r,className:i=``,children:a,iconNode:u,...d},f)=>(0,l.createElement)(`svg`,{ref:f,...c,width:t,height:t,stroke:e,strokeWidth:r?Number(n)*24/Number(t):n,className:o(`lucide`,i),...!a&&!s(d)&&{"aria-hidden":`true`},...d},[...u.map(([e,t])=>(0,l.createElement)(e,t)),...Array.isArray(a)?a:[a]])),d=(e,t)=>{let n=(0,l.forwardRef)(({className:n,...i},s)=>(0,l.createElement)(u,{ref:s,iconNode:t,className:o(`lucide-${r(a(e))}`,`lucide-${e}`,n),...i}));return n.displayName=a(e),n};export{d as b,n as c};