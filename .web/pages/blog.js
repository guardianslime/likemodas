/** @jsxImportSource @emotion/react */


import { Fragment, useCallback, useContext, useEffect, useRef } from "react"
import { ColorModeContext, EventLoopContext, StateContexts } from "$/utils/context"
import { Event, isTrue, refs } from "$/utils/state"
import { Box as RadixThemesBox, Button as RadixThemesButton, DropdownMenu as RadixThemesDropdownMenu, Flex as RadixThemesFlex, Heading as RadixThemesHeading, IconButton as RadixThemesIconButton, Link as RadixThemesLink, Separator as RadixThemesSeparator, Text as RadixThemesText, Theme as RadixThemesTheme } from "@radix-ui/themes"
import NextLink from "next/link"
import { AlignJustify as LucideAlignJustify, Globe as LucideGlobe, LayoutDashboard as LucideLayoutDashboard, LogOut as LucideLogOut, Mail as LucideMail, Mailbox as LucideMailbox, Menu as LucideMenu, Moon as LucideMoon, Newspaper as LucideNewspaper, SquareLibrary as LucideSquareLibrary, Sun as LucideSun, User as LucideUser, X as LucideX } from "lucide-react"
import { Drawer as VaulDrawer } from "vaul"
import theme from "$/utils/theme.js"
import NextHead from "next/head"
import { jsx } from "@emotion/react"



export function Dropdownmenu__item_0135103a5bf381b9d7f74f7b30f7dc66 () {
  
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_click_5c60b26326555421abdb423fe10dafea = useCallback(((...args) => (addEvents([(Event("reflex___state____state.full_stack_python___navigation___state____nav_state.to_home", ({  }), ({  })))], args, ({  })))), [addEvents, Event])



  
  return (
    jsx(
RadixThemesDropdownMenu.Item,
{onClick:on_click_5c60b26326555421abdb423fe10dafea},
"Home"
,)
  )
}

export function Fragment_ef925aabc2d1a07777b4c3dab0074317 () {
  
  const { resolvedColorMode } = useContext(ColorModeContext)





  
  return (
    jsx(
Fragment,
{},
((resolvedColorMode === "light") ? (jsx(
Fragment,
{},
jsx(LucideMoon,{},)
,)) : (jsx(
Fragment,
{},
jsx(LucideSun,{},)
,))),)
  )
}

export function Text_409a4bd687f6b4fcccee7916e6ee61c4 () {
  
  const { resolvedColorMode } = useContext(ColorModeContext)





  
  return (
    jsx(
RadixThemesText,
{as:"p",size:"4"},
((resolvedColorMode === "light") ? "Turn dark mode on" : "Turn light mode on")
,)
  )
}

export function Box_f25d3c09d7bdff8b0c3e58c5f733b7ed () {
  
  const { toggleColorMode } = useContext(ColorModeContext)
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_click_9922dd3e837b9e087c86a2522c2c93f8 = useCallback(toggleColorMode, [addEvents, Event, toggleColorMode])



  
  return (
    jsx(
RadixThemesBox,
{css:({ ["as"] : "button", ["underline"] : "none", ["weight"] : "medium", ["width"] : "100%" }),onClick:on_click_9922dd3e837b9e087c86a2522c2c93f8},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["&:hover"] : ({ ["cursor"] : "pointer", ["background"] : "var(--accent-4)", ["color"] : "var(--accent-11)" }), ["color"] : "var(--accent-11)", ["borderRadius"] : "0.5em", ["width"] : "100%", ["paddingInlineStart"] : "0.5rem", ["paddingInlineEnd"] : "0.5rem", ["paddingTop"] : "0.75rem", ["paddingBottom"] : "0.75rem" }),direction:"row",gap:"3"},
jsx(Fragment_ef925aabc2d1a07777b4c3dab0074317,{},)
,jsx(Text_409a4bd687f6b4fcccee7916e6ee61c4,{},)
,),)
  )
}

export function Dropdownmenu__item_81a2b1073d401a4d60e14f3b0804a346 () {
  
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_click_02556209673b0c9cabeeb5d3671ddcbb = useCallback(((...args) => (addEvents([(Event("reflex___state____state.full_stack_python___navigation___state____nav_state.to_blog", ({  }), ({  })))], args, ({  })))), [addEvents, Event])



  
  return (
    jsx(
RadixThemesDropdownMenu.Item,
{onClick:on_click_02556209673b0c9cabeeb5d3671ddcbb},
"Blog"
,)
  )
}

export function Fragment_949d856a36fb44e2c6cd9cc02626a3ff () {
  
  const reflex___state____state = useContext(StateContexts.reflex___state____state)
  const reflex___state____state__reflex_local_auth___local_auth____local_auth_state = useContext(StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state)





  
  return (
    jsx(
Fragment,
{},
((reflex___state____state.is_hydrated && reflex___state____state__reflex_local_auth___local_auth____local_auth_state.is_authenticated) ? (jsx(Fragment_34734c79ca91d1bb35f4cdc0dbcf088d,{},)
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

export function Dropdownmenu__item_2e94dc784884fede0179af2e6701a2be () {
  
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_click_8a124e67c11dc3962b49d30824e38640 = useCallback(((...args) => (addEvents([(Event("reflex___state____state.full_stack_python___navigation___state____nav_state.to_contact", ({  }), ({  })))], args, ({  })))), [addEvents, Event])



  
  return (
    jsx(
RadixThemesDropdownMenu.Item,
{onClick:on_click_8a124e67c11dc3962b49d30824e38640},
"Contact"
,)
  )
}

export function Box_a3024561c54556fdec0036516b0350d9 () {
  
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_click_e948b8668071b9821449cee5395d4ddb = useCallback(((...args) => (addEvents([(Event("reflex___state____state.full_stack_python___navigation___state____nav_state.to_logout", ({  }), ({  })))], args, ({  })))), [addEvents, Event])



  
  return (
    jsx(
RadixThemesBox,
{css:({ ["as"] : "button", ["underline"] : "none", ["weight"] : "medium", ["width"] : "100%" }),onClick:on_click_e948b8668071b9821449cee5395d4ddb},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["&:hover"] : ({ ["cursor"] : "pointer", ["background"] : "var(--accent-4)", ["color"] : "var(--accent-11)" }), ["color"] : "var(--accent-11)", ["borderRadius"] : "0.5em", ["width"] : "100%", ["paddingInlineStart"] : "0.5rem", ["paddingInlineEnd"] : "0.5rem", ["paddingTop"] : "0.75rem", ["paddingBottom"] : "0.75rem" }),direction:"row",gap:"3"},
jsx(LucideLogOut,{},)
,jsx(
RadixThemesText,
{as:"p",size:"4"},
"Logout"
,),),)
  )
}

export function Link_6d8ef781efad3969e1ad202c69c43883 () {
  
  const { resolvedColorMode } = useContext(ColorModeContext)





  
  return (
    jsx(
RadixThemesLink,
{asChild:true,css:({ ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) }),size:"3"},
jsx(
NextLink,
{href:"https://reflex.dev",passHref:true},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["textAlign"] : "center", ["padding"] : "1em" }),direction:"row",gap:"3"},
"Built with "
,jsx(
"svg",
{"aria-label":"Reflex",css:({ ["fill"] : ((resolvedColorMode === "light") ? "#110F1F" : "white") }),height:"12",role:"img",width:"56",xmlns:"http://www.w3.org/2000/svg"},
jsx("path",{d:"M0 11.5999V0.399902H8.96V4.8799H6.72V2.6399H2.24V4.8799H6.72V7.1199H2.24V11.5999H0ZM6.72 11.5999V7.1199H8.96V11.5999H6.72Z"},)
,jsx("path",{d:"M11.2 11.5999V0.399902H17.92V2.6399H13.44V4.8799H17.92V7.1199H13.44V9.3599H17.92V11.5999H11.2Z"},)
,jsx("path",{d:"M20.16 11.5999V0.399902H26.88V2.6399H22.4V4.8799H26.88V7.1199H22.4V11.5999H20.16Z"},)
,jsx("path",{d:"M29.12 11.5999V0.399902H31.36V9.3599H35.84V11.5999H29.12Z"},)
,jsx("path",{d:"M38.08 11.5999V0.399902H44.8V2.6399H40.32V4.8799H44.8V7.1199H40.32V9.3599H44.8V11.5999H38.08Z"},)
,jsx("path",{d:"M47.04 4.8799V0.399902H49.28V4.8799H47.04ZM53.76 4.8799V0.399902H56V4.8799H53.76ZM49.28 7.1199V4.8799H53.76V7.1199H49.28ZM47.04 11.5999V7.1199H49.28V11.5999H47.04ZM53.76 11.5999V7.1199H56V11.5999H53.76Z"},)
,jsx(
"title",
{},
"Reflex"
,),),),),)
  )
}

export function Dropdownmenu__item_9fe9a971872f647874918ba7a3cd7b39 () {
  
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_click_8776d89d1362aedb583aa24ec66aee08 = useCallback(((...args) => (addEvents([(Event("reflex___state____state.full_stack_python___navigation___state____nav_state.to_login", ({  }), ({  })))], args, ({  })))), [addEvents, Event])



  
  return (
    jsx(
RadixThemesDropdownMenu.Item,
{onClick:on_click_8776d89d1362aedb583aa24ec66aee08},
"Log in"
,)
  )
}

export function Dropdownmenu__item_c240db5f9b11e77b7166baee506fd74a () {
  
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_click_91e7352283792a2032dd308f661fddd4 = useCallback(((...args) => (addEvents([(Event("reflex___state____state.full_stack_python___navigation___state____nav_state.to_register", ({  }), ({  })))], args, ({  })))), [addEvents, Event])



  
  return (
    jsx(
RadixThemesDropdownMenu.Item,
{onClick:on_click_91e7352283792a2032dd308f661fddd4},
"Register"
,)
  )
}

export function Fragment_4735041bcb8d807a384b59168d698006 () {
  
  const { resolvedColorMode } = useContext(ColorModeContext)





  
  return (
    jsx(
Fragment,
{},
((resolvedColorMode === "light") ? (jsx(
Fragment,
{},
jsx(LucideSun,{},)
,)) : (jsx(
Fragment,
{},
jsx(LucideMoon,{},)
,))),)
  )
}

export function Dropdownmenu__item_dfeb4d8d19e41db8abd33bc17298d1c8 () {
  
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_click_3cac78f0c8eca9d0ff9bc316d743bb2b = useCallback(((...args) => (addEvents([(Event("reflex___state____state.full_stack_python___navigation___state____nav_state.to_articles", ({  }), ({  })))], args, ({  })))), [addEvents, Event])



  
  return (
    jsx(
RadixThemesDropdownMenu.Item,
{onClick:on_click_3cac78f0c8eca9d0ff9bc316d743bb2b},
"Articles"
,)
  )
}

export function Flex_874c51d6f75f7e1f8bb405181b345cf0 () {
  
  const reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state = useContext(StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state)





  
  return (
    jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["minHeight"] : "85vh" }),direction:"column",gap:"5"},
jsx(
RadixThemesHeading,
{size:"5"},
"Blog Posts"
,),jsx(
RadixThemesLink,
{asChild:true,css:({ ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) })},
jsx(
NextLink,
{href:"/blog/add",passHref:true},
jsx(
RadixThemesButton,
{},
"New Post"
,),),),reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state.posts.map((post,index_d0ff3c1e8ea50e57)=>(jsx(
RadixThemesBox,
{css:({ ["padding"] : "1em" }),key:index_d0ff3c1e8ea50e57},
jsx(
RadixThemesLink,
{asChild:true,css:({ ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) })},
jsx(
NextLink,
{href:("/blog/"+post["id"]),passHref:true},
jsx(
RadixThemesHeading,
{},
post["title"]
,),jsx(
RadixThemesHeading,
{},
"by "
,post["userinfo"]?.["email"]
,),),),))),)
  )
}

export function Dropdownmenu__item_1fbe7c71954c734735664f498e580e6b () {
  
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_click_58713a7c6318b69ebece54f23e0cd75a = useCallback(((...args) => (addEvents([(Event("reflex___state____state.full_stack_python___navigation___state____nav_state.to_pricing", ({  }), ({  })))], args, ({  })))), [addEvents, Event])



  
  return (
    jsx(
RadixThemesDropdownMenu.Item,
{onClick:on_click_58713a7c6318b69ebece54f23e0cd75a},
"Pricing"
,)
  )
}

export function Text_a985b784da6f758810cf76701d48b67a () {
  
  const reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state = useContext(StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state)





  
  return (
    jsx(
RadixThemesText,
{as:"p",size:"3",weight:"bold"},
(isTrue(reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state.authenticated_username) ? reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state.authenticated_username : "Account")
,)
  )
}

export function Iconbutton_53adde116165ab531c43c5cb8d60c677 () {
  
  const { toggleColorMode } = useContext(ColorModeContext)
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_click_9922dd3e837b9e087c86a2522c2c93f8 = useCallback(toggleColorMode, [addEvents, Event, toggleColorMode])



  
  return (
    jsx(
RadixThemesIconButton,
{css:({ ["padding"] : "6px", ["position"] : "fixed", ["bottom"] : "2rem", ["left"] : "2rem", ["background"] : "transparent", ["color"] : "inherit", ["zIndex"] : "20", ["&:hover"] : ({ ["cursor"] : "pointer" }) }),onClick:on_click_9922dd3e837b9e087c86a2522c2c93f8},
jsx(Fragment_4735041bcb8d807a384b59168d698006,{},)
,)
  )
}

export function Text_f8365c41821e8790dbd1464049a081ca () {
  
  
                useEffect(() => {
                    ((...args) => (addEvents([(Event("reflex___state____state.reflex_local_auth___local_auth____local_auth_state.reflex_local_auth___login____login_state.redir", ({  }), ({  })))], args, ({  }))))()
                    return () => {
                        
                    }
                }, []);
  const [addEvents, connectErrors] = useContext(EventLoopContext);





  
  return (
    jsx(
RadixThemesText,
{as:"p"},
"Loading..."
,)
  )
}

export function Text_d9329775296ebb9d8b450f9e98cbd4b0 () {
  
  const reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state = useContext(StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state)





  
  return (
    jsx(
RadixThemesText,
{as:"p",size:"2",weight:"medium"},
reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state.authenticated_user_info?.["email"]
,)
  )
}

export function Fragment_34734c79ca91d1bb35f4cdc0dbcf088d () {
  
  const reflex___state____state__reflex_local_auth___local_auth____local_auth_state = useContext(StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state)
  const ref_my_content_area_el = useRef(null); refs["ref_my_content_area_el"] = ref_my_content_area_el;
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
,jsx(Fragment_4d9ebd88e2e8e001c2b23f3314a34212,{},)
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
,jsx(Fragment_4d9ebd88e2e8e001c2b23f3314a34212,{},)
,),),),),),),),),jsx(
RadixThemesBox,
{css:({ ["padding"] : "1em", ["width"] : "100%" }),id:"my-content-area-el",ref:ref_my_content_area_el},
jsx(Flex_874c51d6f75f7e1f8bb405181b345cf0,{},)
,jsx(
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
jsx(Flex_874c51d6f75f7e1f8bb405181b345cf0,{},)
,),jsx(
RadixThemesFlex,
{css:({ ["display"] : "flex", ["alignItems"] : "center", ["justifyContent"] : "center", ["width"] : "100%" })},
jsx(Link_6d8ef781efad3969e1ad202c69c43883,{},)
,),jsx(Iconbutton_53adde116165ab531c43c5cb8d60c677,{},)
,))),)
  )
}

export function Fragment_4d9ebd88e2e8e001c2b23f3314a34212 () {
  
  const reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state = useContext(StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state)





  
  return (
    jsx(
Fragment,
{},
(isTrue(reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state.authenticated_user_info) ? (jsx(
Fragment,
{},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["paddingInlineStart"] : "0.5rem", ["paddingInlineEnd"] : "0.5rem", ["width"] : "100%" }),direction:"row",justify:"start",gap:"3"},
jsx(
RadixThemesIconButton,
{css:({ ["padding"] : "6px" }),radius:"full",size:"3"},
jsx(LucideUser,{size:36},)
,),jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"column",justify:"start",gap:"0"},
jsx(
RadixThemesBox,
{css:({ ["width"] : "100%" })},
jsx(Text_a985b784da6f758810cf76701d48b67a,{},)
,jsx(Text_d9329775296ebb9d8b450f9e98cbd4b0,{},)
,),),),)) : (jsx(
Fragment,
{},
""
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
jsx(Fragment_949d856a36fb44e2c6cd9cc02626a3ff,{},)
,),jsx(
NextHead,
{},
jsx(
"title",
{},
"FullStackPython | Blog"
,),jsx("meta",{content:"favicon.ico",property:"og:image"},)
,),)
  )
}
