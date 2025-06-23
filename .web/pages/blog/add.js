/** @jsxImportSource @emotion/react */


import { Fragment, useContext, useRef } from "react"
import { StateContexts } from "$/utils/context"
import { isTrue, refs } from "$/utils/state"
import { Box as RadixThemesBox, Button as RadixThemesButton, DropdownMenu as RadixThemesDropdownMenu, Flex as RadixThemesFlex, Heading as RadixThemesHeading, Link as RadixThemesLink, Separator as RadixThemesSeparator, Text as RadixThemesText, Theme as RadixThemesTheme } from "@radix-ui/themes"
import NextLink from "next/link"
import { AlignJustify as LucideAlignJustify, Globe as LucideGlobe, LayoutDashboard as LucideLayoutDashboard, Mail as LucideMail, Mailbox as LucideMailbox, Menu as LucideMenu, Newspaper as LucideNewspaper, SquareLibrary as LucideSquareLibrary, X as LucideX } from "lucide-react"
import { Box_a3024561c54556fdec0036516b0350d9, Box_f25d3c09d7bdff8b0c3e58c5f733b7ed, Dropdownmenu__item_0135103a5bf381b9d7f74f7b30f7dc66, Dropdownmenu__item_1fbe7c71954c734735664f498e580e6b, Dropdownmenu__item_2e94dc784884fede0179af2e6701a2be, Dropdownmenu__item_81a2b1073d401a4d60e14f3b0804a346, Dropdownmenu__item_9fe9a971872f647874918ba7a3cd7b39, Dropdownmenu__item_c240db5f9b11e77b7166baee506fd74a, Dropdownmenu__item_dfeb4d8d19e41db8abd33bc17298d1c8, Fragment_5ccec3bd2ebf3b045a49657c2326d0f9, Iconbutton_53adde116165ab531c43c5cb8d60c677, Link_6d8ef781efad3969e1ad202c69c43883, Root_30ca9fa28b320364d1c6ecc69b7de571, Text_f8365c41821e8790dbd1464049a081ca } from "$/utils/stateful_components"
import { Drawer as VaulDrawer } from "vaul"
import theme from "$/utils/theme.js"
import NextHead from "next/head"
import { jsx } from "@emotion/react"



export function Fragment_e2d314996009539fdb846fc57fcff17c () {
  
  const reflex___state____state = useContext(StateContexts.reflex___state____state)
  const reflex___state____state__reflex_local_auth___local_auth____local_auth_state = useContext(StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state)





  
  return (
    jsx(
Fragment,
{},
((reflex___state____state.is_hydrated && reflex___state____state__reflex_local_auth___local_auth____local_auth_state.is_authenticated) ? (jsx(Fragment_3631eb6cfb2d02f5ac2af0ed65d2aa65,{},)
) : (jsx(
Fragment,
{},
jsx(
RadixThemesFlex,
{css:({ ["display"] : "flex", ["alignItems"] : "center", ["justifyContent"] : "center" })},
jsx(Text_f8365c41821e8790dbd1464049a081ca,{},)
,),))),)
  )
}

export function Fragment_3631eb6cfb2d02f5ac2af0ed65d2aa65 () {
  
  const reflex___state____state__reflex_local_auth___local_auth____local_auth_state = useContext(StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state)
  const ref_my_content_area_el = useRef(null); refs["ref_my_content_area_el"] = ref_my_content_area_el;
  const ref_my_form_box = useRef(null); refs["ref_my_form_box"] = ref_my_form_box;
  const ref_my_main_nav = useRef(null); refs["ref_my_main_nav"] = ref_my_main_nav;
  const ref_my_navbar_hstack_desktop = useRef(null); refs["ref_my_navbar_hstack_desktop"] = ref_my_navbar_hstack_desktop;





  
  return (
    jsx(
Fragment,
{},
(reflex___state____state__reflex_local_auth___local_auth____local_auth_state.is_authenticated ? (jsx(
Fragment,
{},
jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",direction:"row",gap:"3"},
jsx(
RadixThemesBox,
{},
jsx(
RadixThemesBox,
{css:({ ["@media screen and (min-width: 0)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 30em)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 48em)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 62em)"] : ({ ["display"] : "block" }) })},
jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",css:({ ["paddingInlineStart"] : "1em", ["paddingInlineEnd"] : "1em", ["paddingTop"] : "1.5em", ["paddingBottom"] : "1.5em", ["background"] : "var(--accent-3)", ["height"] : "100vh", ["width"] : "16em" }),direction:"column",gap:"5"},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["paddingInlineStart"] : "0.5rem", ["paddingInlineEnd"] : "0.5rem", ["width"] : "100%" }),direction:"row",justify:"start",gap:"3"},
jsx("img",{css:({ ["width"] : "2.25em", ["height"] : "auto", ["borderRadius"] : "25%" }),src:"/logo.jpg"},)
,jsx(
RadixThemesHeading,
{size:"7",weight:"bold"},
"Reflex"
,),),jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"column",gap:"1"},
jsx(
RadixThemesLink,
{asChild:true,css:({ ["width"] : "100%", ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) }),underline:"none",weight:"medium"},
jsx(
NextLink,
{href:"/",passHref:true},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["&:hover"] : ({ ["background"] : "var(--accent-4)", ["color"] : "var(--accent-11)" }), ["borderRadius"] : "0.5em", ["width"] : "100%", ["paddingInlineStart"] : "0.5rem", ["paddingInlineEnd"] : "0.5rem", ["paddingTop"] : "0.75rem", ["paddingBottom"] : "0.75rem" }),direction:"row",gap:"3"},
jsx(LucideLayoutDashboard,{},)
,jsx(
RadixThemesText,
{as:"p",size:"4"},
"Dashboard"
,),),),),jsx(
RadixThemesLink,
{asChild:true,css:({ ["width"] : "100%", ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) }),underline:"none",weight:"medium"},
jsx(
NextLink,
{href:"/articles",passHref:true},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["&:hover"] : ({ ["background"] : "var(--accent-4)", ["color"] : "var(--accent-11)" }), ["borderRadius"] : "0.5em", ["width"] : "100%", ["paddingInlineStart"] : "0.5rem", ["paddingInlineEnd"] : "0.5rem", ["paddingTop"] : "0.75rem", ["paddingBottom"] : "0.75rem" }),direction:"row",gap:"3"},
jsx(LucideGlobe,{},)
,jsx(
RadixThemesText,
{as:"p",size:"4"},
"Articles"
,),),),),jsx(
RadixThemesLink,
{asChild:true,css:({ ["width"] : "100%", ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) }),underline:"none",weight:"medium"},
jsx(
NextLink,
{href:"/blog",passHref:true},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["&:hover"] : ({ ["background"] : "var(--accent-4)", ["color"] : "var(--accent-11)" }), ["borderRadius"] : "0.5em", ["width"] : "100%", ["paddingInlineStart"] : "0.5rem", ["paddingInlineEnd"] : "0.5rem", ["paddingTop"] : "0.75rem", ["paddingBottom"] : "0.75rem" }),direction:"row",gap:"3"},
jsx(LucideNewspaper,{},)
,jsx(
RadixThemesText,
{as:"p",size:"4"},
"Blog"
,),),),),jsx(
RadixThemesLink,
{asChild:true,css:({ ["width"] : "100%", ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) }),underline:"none",weight:"medium"},
jsx(
NextLink,
{href:"/blog/add",passHref:true},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["&:hover"] : ({ ["background"] : "var(--accent-4)", ["color"] : "var(--accent-11)" }), ["borderRadius"] : "0.5em", ["width"] : "100%", ["paddingInlineStart"] : "0.5rem", ["paddingInlineEnd"] : "0.5rem", ["paddingTop"] : "0.75rem", ["paddingBottom"] : "0.75rem" }),direction:"row",gap:"3"},
jsx(LucideSquareLibrary,{},)
,jsx(
RadixThemesText,
{as:"p",size:"4"},
"Create post"
,),),),),jsx(
RadixThemesLink,
{asChild:true,css:({ ["width"] : "100%", ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) }),underline:"none",weight:"medium"},
jsx(
NextLink,
{href:"/contact",passHref:true},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["&:hover"] : ({ ["background"] : "var(--accent-4)", ["color"] : "var(--accent-11)" }), ["borderRadius"] : "0.5em", ["width"] : "100%", ["paddingInlineStart"] : "0.5rem", ["paddingInlineEnd"] : "0.5rem", ["paddingTop"] : "0.75rem", ["paddingBottom"] : "0.75rem" }),direction:"row",gap:"3"},
jsx(LucideMail,{},)
,jsx(
RadixThemesText,
{as:"p",size:"4"},
"Contact"
,),),),),jsx(
RadixThemesLink,
{asChild:true,css:({ ["width"] : "100%", ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) }),underline:"none",weight:"medium"},
jsx(
NextLink,
{href:"/contact/entries",passHref:true},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["&:hover"] : ({ ["background"] : "var(--accent-4)", ["color"] : "var(--accent-11)" }), ["borderRadius"] : "0.5em", ["width"] : "100%", ["paddingInlineStart"] : "0.5rem", ["paddingInlineEnd"] : "0.5rem", ["paddingTop"] : "0.75rem", ["paddingBottom"] : "0.75rem" }),direction:"row",gap:"3"},
jsx(LucideMailbox,{},)
,jsx(
RadixThemesText,
{as:"p",size:"4"},
"Contact History"
,),),),),),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},)
,jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"column",gap:"5"},
jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"column",gap:"1"},
jsx(Box_f25d3c09d7bdff8b0c3e58c5f733b7ed,{},)
,jsx(Box_a3024561c54556fdec0036516b0350d9,{},)
,),jsx(RadixThemesSeparator,{size:"4"},)
,jsx(Fragment_5ccec3bd2ebf3b045a49657c2326d0f9,{},)
,),),),jsx(
RadixThemesBox,
{css:({ ["padding"] : "1em", ["@media screen and (min-width: 0)"] : ({ ["display"] : "block" }), ["@media screen and (min-width: 30em)"] : ({ ["display"] : "block" }), ["@media screen and (min-width: 48em)"] : ({ ["display"] : "block" }), ["@media screen and (min-width: 62em)"] : ({ ["display"] : "none" }) })},
jsx(
VaulDrawer.Root,
{direction:"left"},
jsx(
VaulDrawer.Trigger,
{asChild:true},
jsx(LucideAlignJustify,{size:30},)
,),jsx(VaulDrawer.Overlay,{css:({ ["position"] : "fixed", ["left"] : "0", ["right"] : "0", ["bottom"] : "0", ["top"] : "0", ["z_index"] : 50, ["background"] : "rgba(0, 0, 0, 0.5)", ["zIndex"] : "5" })},)
,jsx(
VaulDrawer.Portal,
{css:({ ["width"] : "100%" })},
jsx(
RadixThemesTheme,
{css:{...theme.styles.global[':root'], ...theme.styles.global.body}},
jsx(
VaulDrawer.Content,
{css:({ ["left"] : "0", ["right"] : "auto", ["bottom"] : "0", ["top"] : "auto", ["position"] : "fixed", ["z_index"] : 50, ["display"] : "flex", ["height"] : "100%", ["width"] : "20em", ["padding"] : "1.5em", ["background"] : "var(--accent-2)" })},
jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"column",gap:"5"},
jsx(
RadixThemesBox,
{css:({ ["width"] : "100%" })},
jsx(
VaulDrawer.Close,
{asChild:true},
jsx(LucideX,{size:30},)
,),),jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"column",gap:"1"},
jsx(
RadixThemesLink,
{asChild:true,css:({ ["width"] : "100%", ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) }),underline:"none",weight:"medium"},
jsx(
NextLink,
{href:"/",passHref:true},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["&:hover"] : ({ ["background"] : "var(--accent-4)", ["color"] : "var(--accent-11)" }), ["borderRadius"] : "0.5em", ["width"] : "100%", ["paddingInlineStart"] : "0.5rem", ["paddingInlineEnd"] : "0.5rem", ["paddingTop"] : "0.75rem", ["paddingBottom"] : "0.75rem" }),direction:"row",gap:"3"},
jsx(LucideLayoutDashboard,{},)
,jsx(
RadixThemesText,
{as:"p",size:"4"},
"Dashboard"
,),),),),jsx(
RadixThemesLink,
{asChild:true,css:({ ["width"] : "100%", ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) }),underline:"none",weight:"medium"},
jsx(
NextLink,
{href:"/articles",passHref:true},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["&:hover"] : ({ ["background"] : "var(--accent-4)", ["color"] : "var(--accent-11)" }), ["borderRadius"] : "0.5em", ["width"] : "100%", ["paddingInlineStart"] : "0.5rem", ["paddingInlineEnd"] : "0.5rem", ["paddingTop"] : "0.75rem", ["paddingBottom"] : "0.75rem" }),direction:"row",gap:"3"},
jsx(LucideGlobe,{},)
,jsx(
RadixThemesText,
{as:"p",size:"4"},
"Articles"
,),),),),jsx(
RadixThemesLink,
{asChild:true,css:({ ["width"] : "100%", ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) }),underline:"none",weight:"medium"},
jsx(
NextLink,
{href:"/blog",passHref:true},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["&:hover"] : ({ ["background"] : "var(--accent-4)", ["color"] : "var(--accent-11)" }), ["borderRadius"] : "0.5em", ["width"] : "100%", ["paddingInlineStart"] : "0.5rem", ["paddingInlineEnd"] : "0.5rem", ["paddingTop"] : "0.75rem", ["paddingBottom"] : "0.75rem" }),direction:"row",gap:"3"},
jsx(LucideNewspaper,{},)
,jsx(
RadixThemesText,
{as:"p",size:"4"},
"Blog"
,),),),),jsx(
RadixThemesLink,
{asChild:true,css:({ ["width"] : "100%", ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) }),underline:"none",weight:"medium"},
jsx(
NextLink,
{href:"/blog/add",passHref:true},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["&:hover"] : ({ ["background"] : "var(--accent-4)", ["color"] : "var(--accent-11)" }), ["borderRadius"] : "0.5em", ["width"] : "100%", ["paddingInlineStart"] : "0.5rem", ["paddingInlineEnd"] : "0.5rem", ["paddingTop"] : "0.75rem", ["paddingBottom"] : "0.75rem" }),direction:"row",gap:"3"},
jsx(LucideSquareLibrary,{},)
,jsx(
RadixThemesText,
{as:"p",size:"4"},
"Create post"
,),),),),jsx(
RadixThemesLink,
{asChild:true,css:({ ["width"] : "100%", ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) }),underline:"none",weight:"medium"},
jsx(
NextLink,
{href:"/contact",passHref:true},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["&:hover"] : ({ ["background"] : "var(--accent-4)", ["color"] : "var(--accent-11)" }), ["borderRadius"] : "0.5em", ["width"] : "100%", ["paddingInlineStart"] : "0.5rem", ["paddingInlineEnd"] : "0.5rem", ["paddingTop"] : "0.75rem", ["paddingBottom"] : "0.75rem" }),direction:"row",gap:"3"},
jsx(LucideMail,{},)
,jsx(
RadixThemesText,
{as:"p",size:"4"},
"Contact"
,),),),),jsx(
RadixThemesLink,
{asChild:true,css:({ ["width"] : "100%", ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) }),underline:"none",weight:"medium"},
jsx(
NextLink,
{href:"/contact/entries",passHref:true},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["&:hover"] : ({ ["background"] : "var(--accent-4)", ["color"] : "var(--accent-11)" }), ["borderRadius"] : "0.5em", ["width"] : "100%", ["paddingInlineStart"] : "0.5rem", ["paddingInlineEnd"] : "0.5rem", ["paddingTop"] : "0.75rem", ["paddingBottom"] : "0.75rem" }),direction:"row",gap:"3"},
jsx(LucideMailbox,{},)
,jsx(
RadixThemesText,
{as:"p",size:"4"},
"Contact History"
,),),),),),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},)
,jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"column",gap:"5"},
jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"column",gap:"1"},
jsx(Box_f25d3c09d7bdff8b0c3e58c5f733b7ed,{},)
,jsx(Box_a3024561c54556fdec0036516b0350d9,{},)
,),jsx(RadixThemesSeparator,{css:({ ["margin"] : "0" }),size:"4"},)
,jsx(Fragment_5ccec3bd2ebf3b045a49657c2326d0f9,{},)
,),),),),),),),),jsx(
RadixThemesBox,
{css:({ ["padding"] : "1em", ["width"] : "100%" }),id:"my-content-area-el",ref:ref_my_content_area_el},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["minHeight"] : "95vh" }),direction:"column",gap:"5"},
jsx(
RadixThemesHeading,
{size:"9"},
"New Blog Post"
,),jsx(
RadixThemesBox,
{css:({ ["@media screen and (min-width: 0)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 30em)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 48em)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 62em)"] : ({ ["display"] : "block" }) })},
jsx(
RadixThemesBox,
{css:({ ["width"] : "50vw" })},
jsx(Root_30ca9fa28b320364d1c6ecc69b7de571,{},)
,),),jsx(
RadixThemesBox,
{css:({ ["@media screen and (min-width: 0)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 30em)"] : ({ ["display"] : "block" }), ["@media screen and (min-width: 48em)"] : ({ ["display"] : "block" }), ["@media screen and (min-width: 62em)"] : ({ ["display"] : "none" }) })},
jsx(
RadixThemesBox,
{css:({ ["width"] : "75vw" })},
jsx(Root_30ca9fa28b320364d1c6ecc69b7de571,{},)
,),),jsx(
RadixThemesBox,
{css:({ ["@media screen and (min-width: 0)"] : ({ ["display"] : "block" }), ["@media screen and (min-width: 30em)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 48em)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 62em)"] : ({ ["display"] : "none" }) })},
jsx(
RadixThemesBox,
{css:({ ["width"] : "85vw" }),id:"my-form-box",ref:ref_my_form_box},
jsx(Root_30ca9fa28b320364d1c6ecc69b7de571,{},)
,),),),jsx(
RadixThemesFlex,
{css:({ ["display"] : "flex", ["alignItems"] : "center", ["justifyContent"] : "center", ["width"] : "100%" })},
jsx(Link_6d8ef781efad3969e1ad202c69c43883,{},)
,),),),)) : (jsx(
Fragment,
{},
jsx(
RadixThemesBox,
{css:({ ["background"] : "var(--accent-3)", ["padding"] : "1em", ["width"] : "100%" }),id:"my-main-nav",ref:ref_my_main_nav},
jsx(
RadixThemesBox,
{css:({ ["@media screen and (min-width: 0)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 30em)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 48em)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 62em)"] : ({ ["display"] : "block" }) })},
jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",css:({ ["alignItems"] : "center" }),direction:"row",id:"my-navbar-hstack-desktop",justify:"between",ref:ref_my_navbar_hstack_desktop,gap:"3"},
jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",css:({ ["alignItems"] : "center" }),direction:"row",gap:"3"},
jsx(
RadixThemesLink,
{asChild:true,css:({ ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) })},
jsx(
NextLink,
{href:"/",passHref:true},
jsx("img",{css:({ ["width"] : "2.25em", ["height"] : "auto", ["borderRadius"] : "25%" }),src:"/logo.jpg"},)
,),),jsx(
RadixThemesLink,
{asChild:true,css:({ ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) })},
jsx(
NextLink,
{href:"/",passHref:true},
jsx(
RadixThemesHeading,
{size:"7",weight:"bold"},
"Reflex"
,),),),),jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",direction:"row",gap:"5"},
jsx(
RadixThemesLink,
{asChild:true,css:({ ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) })},
jsx(
NextLink,
{href:"/",passHref:true},
jsx(
RadixThemesText,
{as:"p",size:"4",weight:"medium"},
"Home"
,),),),jsx(
RadixThemesLink,
{asChild:true,css:({ ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) })},
jsx(
NextLink,
{href:"/about",passHref:true},
jsx(
RadixThemesText,
{as:"p",size:"4",weight:"medium"},
"About"
,),),),jsx(
RadixThemesLink,
{asChild:true,css:({ ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) })},
jsx(
NextLink,
{href:"/articles",passHref:true},
jsx(
RadixThemesText,
{as:"p",size:"4",weight:"medium"},
"Articles"
,),),),jsx(
RadixThemesLink,
{asChild:true,css:({ ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) })},
jsx(
NextLink,
{href:"/pricing",passHref:true},
jsx(
RadixThemesText,
{as:"p",size:"4",weight:"medium"},
"Pricing"
,),),),jsx(
RadixThemesLink,
{asChild:true,css:({ ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) })},
jsx(
NextLink,
{href:"/contact",passHref:true},
jsx(
RadixThemesText,
{as:"p",size:"4",weight:"medium"},
"Contact"
,),),),),jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",direction:"row",justify:"end",gap:"4"},
jsx(
RadixThemesLink,
{asChild:true,css:({ ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) })},
jsx(
NextLink,
{href:"/register",passHref:true},
jsx(
RadixThemesButton,
{size:"3",variant:"outline"},
"Register"
,),),),jsx(
RadixThemesLink,
{asChild:true,css:({ ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) })},
jsx(
NextLink,
{href:"/login",passHref:true},
jsx(
RadixThemesButton,
{size:"3",variant:"outline"},
"Login"
,),),),),),),jsx(
RadixThemesBox,
{css:({ ["@media screen and (min-width: 0)"] : ({ ["display"] : "block" }), ["@media screen and (min-width: 30em)"] : ({ ["display"] : "block" }), ["@media screen and (min-width: 48em)"] : ({ ["display"] : "block" }), ["@media screen and (min-width: 62em)"] : ({ ["display"] : "none" }) })},
jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",css:({ ["alignItems"] : "center" }),direction:"row",justify:"between",gap:"3"},
jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",css:({ ["alignItems"] : "center" }),direction:"row",gap:"3"},
jsx("img",{css:({ ["width"] : "2em", ["height"] : "auto", ["borderRadius"] : "25%" }),src:"/logo.jpg"},)
,jsx(
RadixThemesHeading,
{size:"6",weight:"bold"},
"Reflex"
,),),jsx(
RadixThemesDropdownMenu.Root,
{css:({ ["justify"] : "end" })},
jsx(
RadixThemesDropdownMenu.Trigger,
{},
jsx(LucideMenu,{size:30},)
,),jsx(
RadixThemesDropdownMenu.Content,
{},
jsx(Dropdownmenu__item_0135103a5bf381b9d7f74f7b30f7dc66,{},)
,jsx(Dropdownmenu__item_dfeb4d8d19e41db8abd33bc17298d1c8,{},)
,jsx(Dropdownmenu__item_81a2b1073d401a4d60e14f3b0804a346,{},)
,jsx(Dropdownmenu__item_1fbe7c71954c734735664f498e580e6b,{},)
,jsx(Dropdownmenu__item_2e94dc784884fede0179af2e6701a2be,{},)
,jsx(RadixThemesDropdownMenu.Separator,{},)
,jsx(Dropdownmenu__item_9fe9a971872f647874918ba7a3cd7b39,{},)
,jsx(Dropdownmenu__item_c240db5f9b11e77b7166baee506fd74a,{},)
,),),),),),jsx(
RadixThemesBox,
{css:({ ["padding"] : "1em", ["width"] : "100%" }),id:"my-content-area-el",ref:ref_my_content_area_el},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["minHeight"] : "95vh" }),direction:"column",gap:"5"},
jsx(
RadixThemesHeading,
{size:"9"},
"New Blog Post"
,),jsx(
RadixThemesBox,
{css:({ ["@media screen and (min-width: 0)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 30em)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 48em)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 62em)"] : ({ ["display"] : "block" }) })},
jsx(
RadixThemesBox,
{css:({ ["width"] : "50vw" })},
jsx(Root_30ca9fa28b320364d1c6ecc69b7de571,{},)
,),),jsx(
RadixThemesBox,
{css:({ ["@media screen and (min-width: 0)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 30em)"] : ({ ["display"] : "block" }), ["@media screen and (min-width: 48em)"] : ({ ["display"] : "block" }), ["@media screen and (min-width: 62em)"] : ({ ["display"] : "none" }) })},
jsx(
RadixThemesBox,
{css:({ ["width"] : "75vw" })},
jsx(Root_30ca9fa28b320364d1c6ecc69b7de571,{},)
,),),jsx(
RadixThemesBox,
{css:({ ["@media screen and (min-width: 0)"] : ({ ["display"] : "block" }), ["@media screen and (min-width: 30em)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 48em)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 62em)"] : ({ ["display"] : "none" }) })},
jsx(
RadixThemesBox,
{css:({ ["width"] : "85vw" }),id:"my-form-box",ref:ref_my_form_box},
jsx(Root_30ca9fa28b320364d1c6ecc69b7de571,{},)
,),),),),jsx(
RadixThemesFlex,
{css:({ ["display"] : "flex", ["alignItems"] : "center", ["justifyContent"] : "center", ["width"] : "100%" })},
jsx(Link_6d8ef781efad3969e1ad202c69c43883,{},)
,),jsx(Iconbutton_53adde116165ab531c43c5cb8d60c677,{},)
,))),)
  )
}

export default function Component() {
    




  return (
    jsx(
Fragment,
{},
jsx(
Fragment,
{},
jsx(Fragment_e2d314996009539fdb846fc57fcff17c,{},)
,),jsx(
NextHead,
{},
jsx(
"title",
{},
"FullStackPython | Add"
,),jsx("meta",{content:"favicon.ico",property:"og:image"},)
,),)
  )
}
