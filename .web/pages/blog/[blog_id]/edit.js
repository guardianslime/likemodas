/** @jsxImportSource @emotion/react */


import { Fragment, useCallback, useContext, useEffect, useRef } from "react"
import { ColorModeContext, EventLoopContext, StateContexts } from "$/utils/context"
import { Event, getRefValue, getRefValues, isNotNullOrUndefined, isTrue, refs } from "$/utils/state"
import { Box as RadixThemesBox, Button as RadixThemesButton, DropdownMenu as RadixThemesDropdownMenu, Flex as RadixThemesFlex, Heading as RadixThemesHeading, IconButton as RadixThemesIconButton, Link as RadixThemesLink, Separator as RadixThemesSeparator, Switch as RadixThemesSwitch, Text as RadixThemesText, TextArea as RadixThemesTextArea, TextField as RadixThemesTextField, Theme as RadixThemesTheme } from "@radix-ui/themes"
import NextLink from "next/link"
import { AlignJustify as LucideAlignJustify, Globe as LucideGlobe, LayoutDashboard as LucideLayoutDashboard, LogOut as LucideLogOut, Mail as LucideMail, Mailbox as LucideMailbox, Menu as LucideMenu, Moon as LucideMoon, Newspaper as LucideNewspaper, SquareLibrary as LucideSquareLibrary, Sun as LucideSun, User as LucideUser, X as LucideX } from "lucide-react"
import { Drawer as VaulDrawer } from "vaul"
import theme from "$/utils/theme.js"
import { Root as RadixFormRoot } from "@radix-ui/react-form"
import { DebounceInput } from "react-debounce-input"
import NextHead from "next/head"
import { jsx } from "@emotion/react"



export function Fragment_ca347cf4b705e0ad50abe3e04075ae60 () {
  
  const reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state = useContext(StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state)





  
  return (
    jsx(
Fragment,
{},
(reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state.post_publish_active ? (jsx(
Fragment,
{},
jsx(
RadixThemesBox,
{css:({ ["width"] : "100%" })},
jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},
jsx(Textfield__root_b87ea0fbdf5414ffeb3dd83706c673ec,{},)
,jsx(Textfield__root_0236b08bfd5fd58a07489aac880f401d,{},)
,),),)) : (jsx(Fragment,{},)
)),)
  )
}

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

export function Heading_65bf7fc047c25438e6d12ad5f4856ae9 () {
  
  const reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state = useContext(StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state)





  
  return (
    jsx(
RadixThemesHeading,
{size:"9"},
"Editing "
,reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state.post?.["title"]
,)
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

export function Textfield__root_53d9132ffba40ef2a33a51466df3225f () {
  
  const reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state = useContext(StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state)





  
  return (
    jsx(RadixThemesTextField.Root,{name:"post_id",type:"hidden",value:(isNotNullOrUndefined((((reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state.post?.["id"] !== null) && (reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state.post?.["id"] !== undefined)) ? reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state.post?.["id"] : "")) ? (((reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state.post?.["id"] !== null) && (reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state.post?.["id"] !== undefined)) ? reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state.post?.["id"] : "") : "")},)

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

export function Textfield__root_8d76a480ed0096d8ff526fc8315dc281 () {
  
  const reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state = useContext(StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state)





  
  return (
    jsx(RadixThemesTextField.Root,{css:({ ["width"] : "100%" }),defaultValue:reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state.post?.["title"],name:"title",placeholder:"Title",required:true,type:"text"},)

  )
}

export function Textfield__root_b87ea0fbdf5414ffeb3dd83706c673ec () {
  
  const reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_edit_form_state = useContext(StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_edit_form_state)





  
  return (
    jsx(RadixThemesTextField.Root,{css:({ ["width"] : "100%" }),defaultValue:reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_edit_form_state.publish_display_date,name:"publish_date",type:"date"},)

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

export function Fragment_6b99e9c7b352819ceb4120d957fcf0b3 () {
  
  const reflex___state____state = useContext(StateContexts.reflex___state____state)
  const reflex___state____state__reflex_local_auth___local_auth____local_auth_state = useContext(StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state)





  
  return (
    jsx(
Fragment,
{},
((reflex___state____state.is_hydrated && reflex___state____state__reflex_local_auth___local_auth____local_auth_state.is_authenticated) ? (jsx(Fragment_0168e7e6bfcc0d3d893fda32354825c8,{},)
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

export function Fragment_ad405b41a0d0178dc36ae3c2616e4764 () {
  
  const reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state = useContext(StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state)
  const ref_my_form_box = useRef(null); refs["ref_my_form_box"] = ref_my_form_box;





  
  return (
    jsx(
Fragment,
{},
(isTrue(reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state.post) ? (jsx(
Fragment,
{},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["minHeight"] : "95vh" }),direction:"column",gap:"5"},
jsx(Heading_65bf7fc047c25438e6d12ad5f4856ae9,{},)
,jsx(
RadixThemesBox,
{css:({ ["@media screen and (min-width: 0)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 30em)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 48em)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 62em)"] : ({ ["display"] : "block" }) })},
jsx(
RadixThemesBox,
{css:({ ["width"] : "50vw" })},
jsx(Root_fd05b1e7196baf69e4e8cb99106e4452,{},)
,),),jsx(
RadixThemesBox,
{css:({ ["@media screen and (min-width: 0)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 30em)"] : ({ ["display"] : "block" }), ["@media screen and (min-width: 48em)"] : ({ ["display"] : "block" }), ["@media screen and (min-width: 62em)"] : ({ ["display"] : "none" }) })},
jsx(
RadixThemesBox,
{css:({ ["width"] : "75vw" })},
jsx(Root_fd05b1e7196baf69e4e8cb99106e4452,{},)
,),),jsx(
RadixThemesBox,
{css:({ ["@media screen and (min-width: 0)"] : ({ ["display"] : "block" }), ["@media screen and (min-width: 30em)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 48em)"] : ({ ["display"] : "none" }), ["@media screen and (min-width: 62em)"] : ({ ["display"] : "none" }) })},
jsx(
RadixThemesBox,
{css:({ ["width"] : "85vw" }),id:"my-form-box",ref:ref_my_form_box},
jsx(Root_fd05b1e7196baf69e4e8cb99106e4452,{},)
,),),),)) : (jsx(
Fragment,
{},
jsx(
RadixThemesFlex,
{align:"center",className:"rx-Stack",css:({ ["minHeight"] : "85vh" }),direction:"row",gap:"5"},
jsx(
RadixThemesHeading,
{},
"Blog PostNot Found"
,),),))),)
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

export function Debounceinput_c99a0c905ca64bd58399c59c37fcd3d5 () {
  
  const reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state = useContext(StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state)
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_change_b8464a9bb9134182ab4968a944f1795f = useCallback(((_e) => (addEvents([(Event("reflex___state____state.reflex_local_auth___local_auth____local_auth_state.full_stack_python___auth___state____session_state.full_stack_python___blog___state____blog_post_state.set_post_content", ({ ["value"] : _e["target"]["value"] }), ({  })))], [_e], ({  })))), [addEvents, Event])



  
  return (
    jsx(DebounceInput,{css:({ ["height"] : "50vh", ["width"] : "100%" }),debounceTimeout:300,element:RadixThemesTextArea,name:"content",onChange:on_change_b8464a9bb9134182ab4968a944f1795f,placeholder:"Your message",required:true,value:reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state.post_content},)

  )
}

export function Switch_187881db425609111c31bbfd136a3277 () {
  
  const reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state = useContext(StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state)
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_change_0fcb3cdba4563238f47aba51054032be = useCallback(((_ev_0) => (addEvents([(Event("reflex___state____state.reflex_local_auth___local_auth____local_auth_state.full_stack_python___auth___state____session_state.full_stack_python___blog___state____blog_post_state.set_post_publish_active", ({ ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, Event])



  
  return (
    jsx(RadixThemesSwitch,{defaultChecked:reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state.post_publish_active,name:"publish_active",onCheckedChange:on_change_0fcb3cdba4563238f47aba51054032be},)

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

export function Fragment_0168e7e6bfcc0d3d893fda32354825c8 () {
  
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
jsx(Fragment_ad405b41a0d0178dc36ae3c2616e4764,{},)
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
jsx(Fragment_ad405b41a0d0178dc36ae3c2616e4764,{},)
,),jsx(
RadixThemesFlex,
{css:({ ["display"] : "flex", ["alignItems"] : "center", ["justifyContent"] : "center", ["width"] : "100%" })},
jsx(Link_6d8ef781efad3969e1ad202c69c43883,{},)
,),jsx(Iconbutton_53adde116165ab531c43c5cb8d60c677,{},)
,))),)
  )
}

export function Root_fd05b1e7196baf69e4e8cb99106e4452 () {
  
  const [addEvents, connectErrors] = useContext(EventLoopContext);

  
    const handleSubmit_0e4f365c4016e2a056234986cb144652 = useCallback((ev) => {
        const $form = ev.target
        ev.preventDefault()
        const form_data = {...Object.fromEntries(new FormData($form).entries()), ...({  })};

        (((...args) => (addEvents([(Event("reflex___state____state.reflex_local_auth___local_auth____local_auth_state.full_stack_python___auth___state____session_state.full_stack_python___blog___state____blog_post_state.full_stack_python___blog___state____blog_edit_form_state.handle_submit", ({ ["form_data"] : form_data }), ({  })))], args, ({  }))))(ev));

        if (false) {
            $form.reset()
        }
    })
    




  
  return (
    jsx(
RadixFormRoot,
{className:"Root ",css:({ ["width"] : "100%" }),onSubmit:handleSubmit_0e4f365c4016e2a056234986cb144652},
jsx(
RadixThemesBox,
{css:({ ["display"] : "none" })},
jsx(Textfield__root_53d9132ffba40ef2a33a51466df3225f,{},)
,),jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",direction:"column",gap:"3"},
jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},
jsx(Textfield__root_8d76a480ed0096d8ff526fc8315dc281,{},)
,),jsx(Debounceinput_c99a0c905ca64bd58399c59c37fcd3d5,{},)
,jsx(
RadixThemesFlex,
{gap:"2"},
jsx(Switch_187881db425609111c31bbfd136a3277,{},)
,jsx(
RadixThemesText,
{as:"p"},
"Publish Active"
,),),jsx(Fragment_ca347cf4b705e0ad50abe3e04075ae60,{},)
,jsx(
RadixThemesButton,
{type:"submit"},
"Submit"
,),),)
  )
}

export function Textfield__root_0236b08bfd5fd58a07489aac880f401d () {
  
  const reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_edit_form_state = useContext(StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_edit_form_state)





  
  return (
    jsx(RadixThemesTextField.Root,{css:({ ["width"] : "100%" }),defaultValue:reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_edit_form_state.publish_display_time,name:"publish_time",type:"time"},)

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
jsx(Fragment_6b99e9c7b352819ceb4120d957fcf0b3,{},)
,),jsx(
NextHead,
{},
jsx(
"title",
{},
"FullStackPython | Edit"
,),jsx("meta",{content:"favicon.ico",property:"og:image"},)
,),)
  )
}
