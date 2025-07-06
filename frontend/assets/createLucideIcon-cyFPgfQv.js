import{a as s}from"./chunk-NL6KNZEE-nTYo1-AP.js";import{o as y,v as h,C as g,y as w,l as b,B as C,f as $,w as O,g as E,h as _,i as x,k,q as A}from"./button-Bj1D3b9c.js";var d=function(){return d=Object.assign||function(t){for(var n,e=1,o=arguments.length;e<o;e++){n=arguments[e];for(var a in n)Object.prototype.hasOwnProperty.call(n,a)&&(t[a]=n[a])}return t},d.apply(this,arguments)};function F(r,t){var n={};for(var e in r)Object.prototype.hasOwnProperty.call(r,e)&&t.indexOf(e)<0&&(n[e]=r[e]);if(r!=null&&typeof Object.getOwnPropertySymbols=="function")for(var o=0,e=Object.getOwnPropertySymbols(r);o<e.length;o++)t.indexOf(e[o])<0&&Object.prototype.propertyIsEnumerable.call(r,e[o])&&(n[e[o]]=r[e[o]]);return n}function G(r,t,n,e){function o(a){return a instanceof n?a:new n(function(l){l(a)})}return new(n||(n=Promise))(function(a,l){function u(c){try{i(e.next(c))}catch(f){l(f)}}function p(c){try{i(e.throw(c))}catch(f){l(f)}}function i(c){c.done?a(c.value):o(c.value).then(u,p)}i((e=e.apply(r,t||[])).next())})}function H(r,t,n){if(n||arguments.length===2)for(var e=0,o=t.length,a;e<o;e++)(a||!(e in t))&&(a||(a=Array.prototype.slice.call(t,0,e)),a[e]=t[e]);return r.concat(a||Array.prototype.slice.call(t))}const N=["div","span"],j=["none","inline","inline-block","block","contents"],L={as:{type:"enum",values:N,default:"div"},...y,display:{type:"enum",className:"rt-r-display",values:j,responsive:!0}},B=s.forwardRef((r,t)=>{const{className:n,asChild:e,as:o="div",...a}=h(r,L,C,b);return s.createElement(e?g:o,{...a,ref:t,className:w("rt-Box",n)})});B.displayName="Box";const S=["1","2","3","4","5","6","7","8","9"],P=["auto","always","hover","none"],R={...y,size:{type:"enum",className:"rt-r-size",values:S,responsive:!0},...k,...x,..._,...E,underline:{type:"enum",className:"rt-underline",values:P,default:"auto"},...O,...$},I=s.forwardRef((r,t)=>{const{children:n,className:e,color:o,asChild:a,...l}=h(r,R);return s.createElement(A,{...l,"data-accent-color":o,ref:t,asChild:!0,className:w("rt-reset","rt-Link",e)},a?n:s.createElement("a",null,n))});I.displayName="Link";/**
 * @license lucide-react v0.511.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const U=r=>r.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase(),W=r=>r.replace(/^([A-Z])|[\s-_]+(\w)/g,(t,n,e)=>e?e.toUpperCase():n.toLowerCase()),m=r=>{const t=W(r);return t.charAt(0).toUpperCase()+t.slice(1)},v=(...r)=>r.filter((t,n,e)=>!!t&&t.trim()!==""&&e.indexOf(t)===n).join(" ").trim(),Z=r=>{for(const t in r)if(t.startsWith("aria-")||t==="role"||t==="title")return!0};/**
 * @license lucide-react v0.511.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var q={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"};/**
 * @license lucide-react v0.511.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const z=s.forwardRef(({color:r="currentColor",size:t=24,strokeWidth:n=2,absoluteStrokeWidth:e,className:o="",children:a,iconNode:l,...u},p)=>s.createElement("svg",{ref:p,...q,width:t,height:t,stroke:r,strokeWidth:e?Number(n)*24/Number(t):n,className:v("lucide",o),...!a&&!Z(u)&&{"aria-hidden":"true"},...u},[...l.map(([i,c])=>s.createElement(i,c)),...Array.isArray(a)?a:[a]]));/**
 * @license lucide-react v0.511.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const J=(r,t)=>{const n=s.forwardRef(({className:e,...o},a)=>s.createElement(z,{ref:a,iconNode:t,className:v(`lucide-${U(m(r))}`,`lucide-${r}`,e),...o}));return n.displayName=m(r),n};export{d as _,F as a,H as b,J as c,G as d,I as e,B as p};
