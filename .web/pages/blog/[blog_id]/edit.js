/** @jsxImportSource @emotion/react */


import { Fragment, useCallback, useContext, useEffect, useRef } from "react"
import { ColorModeContext, EventLoopContext, StateContexts } from "/utils/context"
import { Event, getBackendURL, getRefValue, getRefValues, isTrue, refs } from "/utils/state"
import { AlignJustifyIcon as LucideAlignJustifyIcon, GlobeIcon as LucideGlobeIcon, LayoutDashboardIcon as LucideLayoutDashboardIcon, LogOutIcon as LucideLogOutIcon, MailboxIcon as LucideMailboxIcon, MailIcon as LucideMailIcon, MenuIcon as LucideMenuIcon, MoonIcon as LucideMoonIcon, NewspaperIcon as LucideNewspaperIcon, SquareLibraryIcon as LucideSquareLibraryIcon, SunIcon as LucideSunIcon, UserIcon as LucideUserIcon, WifiOffIcon as LucideWifiOffIcon, XIcon as LucideXIcon } from "lucide-react"
import { keyframes } from "@emotion/react"
import { Box as RadixThemesBox, Button as RadixThemesButton, Dialog as RadixThemesDialog, DropdownMenu as RadixThemesDropdownMenu, Flex as RadixThemesFlex, Heading as RadixThemesHeading, IconButton as RadixThemesIconButton, Link as RadixThemesLink, Separator as RadixThemesSeparator, Switch as RadixThemesSwitch, Text as RadixThemesText, TextArea as RadixThemesTextArea, TextField as RadixThemesTextField, Theme as RadixThemesTheme } from "@radix-ui/themes"
import env from "/env.json"
import NextLink from "next/link"
import { Drawer as VaulDrawer } from "vaul"
import "@radix-ui/themes/styles.css"
import theme from "/utils/theme.js"
import { Root as RadixFormRoot } from "@radix-ui/react-form"
import { DebounceInput } from "react-debounce-input"
import NextHead from "next/head"



export function Fragment_b3f78fefb515fde8e224782a994a7310 () {
  const state = useContext(StateContexts.state)
  const state__local_auth_state = useContext(StateContexts.state__local_auth_state)
  const [ colorMode, toggleColorMode ] = useContext(ColorModeContext)
  const [addEvents, connectErrors] = useContext(EventLoopContext);
  const state__local_auth_state__session_state = useContext(StateContexts.state__local_auth_state__session_state)
  const ref_my_content_area_el = useRef(null); refs['ref_my_content_area_el'] = ref_my_content_area_el;
  const state__local_auth_state__session_state__blog_post_state = useContext(StateContexts.state__local_auth_state__session_state__blog_post_state)
  const state__local_auth_state__session_state__blog_post_state__blog_edit_form_state = useContext(StateContexts.state__local_auth_state__session_state__blog_post_state__blog_edit_form_state)
  const ref_my_form_box = useRef(null); refs['ref_my_form_box'] = ref_my_form_box;
  const ref_my_main_nav = useRef(null); refs['ref_my_main_nav'] = ref_my_main_nav;
  const ref_my_navbar_hstack_desktop = useRef(null); refs['ref_my_navbar_hstack_desktop'] = ref_my_navbar_hstack_desktop;
  
                useEffect(() => {
                    addEvents([Event("state.local_auth_state.login_state.redir", {})])
                    return () => {
                        
                    }
                }, []);


  
    const handleSubmit_54e581d5da48387adcf7cd9a2b15226c = useCallback((ev) => {
        const $form = ev.target
        ev.preventDefault()
        const form_data = {...Object.fromEntries(new FormData($form).entries()), ...{}}

        addEvents([Event("state.local_auth_state.session_state.blog_post_state.blog_edit_form_state.handle_submit", {form_data:form_data})])

        if (false) {
            $form.reset()
        }
    })
    

  return (
    <Fragment>
  {isTrue(((state.is_hydrated) && (state__local_auth_state.is_authenticated))) ? (
  <Fragment>
  {isTrue(state__local_auth_state.is_authenticated) ? (
  <Fragment>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} direction={`row`} gap={`3`}>
  <RadixThemesBox>
  <RadixThemesBox css={{"@media screen and (min-width: 0)": {"display": "none"}, "@media screen and (min-width: 30em)": {"display": "none"}, "@media screen and (min-width: 48em)": {"display": "none"}, "@media screen and (min-width: 62em)": {"display": "block"}}}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"paddingInlineStart": "1em", "paddingInlineEnd": "1em", "paddingTop": "1.5em", "paddingBottom": "1.5em", "background": "var(--accent-3)", "height": "100vh", "width": "16em"}} direction={`column`} gap={`5`}>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"paddingInlineStart": "0.5rem", "paddingInlineEnd": "0.5rem", "width": "100%"}} direction={`row`} justify={`start`} gap={`3`}>
  <img css={{"width": "2.25em", "height": "auto", "borderRadius": "25%"}} src={`/logo.jpg`}/>
  <RadixThemesHeading size={`7`} weight={`bold`}>
  {`Reflex`}
</RadixThemesHeading>
</RadixThemesFlex>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`column`} gap={`1`}>
  <RadixThemesLink asChild={true} css={{"width": "100%", "&:hover": {"color": "var(--accent-8)"}}} underline={`none`} weight={`medium`}>
  <NextLink href={`/`} passHref={true}>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"&:hover": {"background": "var(--accent-4)", "color": "var(--accent-11)"}, "border-radius": "0.5em", "width": "100%", "paddingInlineStart": "0.5rem", "paddingInlineEnd": "0.5rem", "paddingTop": "0.75rem", "paddingBottom": "0.75rem"}} direction={`row`} gap={`3`}>
  <LucideLayoutDashboardIcon css={{"color": "var(--current-color)"}}/>
  <RadixThemesText as={`p`} size={`4`}>
  {`Dashboard`}
</RadixThemesText>
</RadixThemesFlex>
</NextLink>
</RadixThemesLink>
  <RadixThemesLink asChild={true} css={{"width": "100%", "&:hover": {"color": "var(--accent-8)"}}} underline={`none`} weight={`medium`}>
  <NextLink href={`/articles`} passHref={true}>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"&:hover": {"background": "var(--accent-4)", "color": "var(--accent-11)"}, "border-radius": "0.5em", "width": "100%", "paddingInlineStart": "0.5rem", "paddingInlineEnd": "0.5rem", "paddingTop": "0.75rem", "paddingBottom": "0.75rem"}} direction={`row`} gap={`3`}>
  <LucideGlobeIcon css={{"color": "var(--current-color)"}}/>
  <RadixThemesText as={`p`} size={`4`}>
  {`Articles`}
</RadixThemesText>
</RadixThemesFlex>
</NextLink>
</RadixThemesLink>
  <RadixThemesLink asChild={true} css={{"width": "100%", "&:hover": {"color": "var(--accent-8)"}}} underline={`none`} weight={`medium`}>
  <NextLink href={`/blog`} passHref={true}>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"&:hover": {"background": "var(--accent-4)", "color": "var(--accent-11)"}, "border-radius": "0.5em", "width": "100%", "paddingInlineStart": "0.5rem", "paddingInlineEnd": "0.5rem", "paddingTop": "0.75rem", "paddingBottom": "0.75rem"}} direction={`row`} gap={`3`}>
  <LucideNewspaperIcon css={{"color": "var(--current-color)"}}/>
  <RadixThemesText as={`p`} size={`4`}>
  {`Blog`}
</RadixThemesText>
</RadixThemesFlex>
</NextLink>
</RadixThemesLink>
  <RadixThemesLink asChild={true} css={{"width": "100%", "&:hover": {"color": "var(--accent-8)"}}} underline={`none`} weight={`medium`}>
  <NextLink href={`/blog/add`} passHref={true}>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"&:hover": {"background": "var(--accent-4)", "color": "var(--accent-11)"}, "border-radius": "0.5em", "width": "100%", "paddingInlineStart": "0.5rem", "paddingInlineEnd": "0.5rem", "paddingTop": "0.75rem", "paddingBottom": "0.75rem"}} direction={`row`} gap={`3`}>
  <LucideSquareLibraryIcon css={{"color": "var(--current-color)"}}/>
  <RadixThemesText as={`p`} size={`4`}>
  {`Create post`}
</RadixThemesText>
</RadixThemesFlex>
</NextLink>
</RadixThemesLink>
  <RadixThemesLink asChild={true} css={{"width": "100%", "&:hover": {"color": "var(--accent-8)"}}} underline={`none`} weight={`medium`}>
  <NextLink href={`/contact`} passHref={true}>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"&:hover": {"background": "var(--accent-4)", "color": "var(--accent-11)"}, "border-radius": "0.5em", "width": "100%", "paddingInlineStart": "0.5rem", "paddingInlineEnd": "0.5rem", "paddingTop": "0.75rem", "paddingBottom": "0.75rem"}} direction={`row`} gap={`3`}>
  <LucideMailIcon css={{"color": "var(--current-color)"}}/>
  <RadixThemesText as={`p`} size={`4`}>
  {`Contact`}
</RadixThemesText>
</RadixThemesFlex>
</NextLink>
</RadixThemesLink>
  <RadixThemesLink asChild={true} css={{"width": "100%", "&:hover": {"color": "var(--accent-8)"}}} underline={`none`} weight={`medium`}>
  <NextLink href={`/contact/entries`} passHref={true}>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"&:hover": {"background": "var(--accent-4)", "color": "var(--accent-11)"}, "border-radius": "0.5em", "width": "100%", "paddingInlineStart": "0.5rem", "paddingInlineEnd": "0.5rem", "paddingTop": "0.75rem", "paddingBottom": "0.75rem"}} direction={`row`} gap={`3`}>
  <LucideMailboxIcon css={{"color": "var(--current-color)"}}/>
  <RadixThemesText as={`p`} size={`4`}>
  {`Contact History`}
</RadixThemesText>
</RadixThemesFlex>
</NextLink>
</RadixThemesLink>
</RadixThemesFlex>
  <RadixThemesFlex css={{"flex": 1, "justifySelf": "stretch", "alignSelf": "stretch"}}/>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`column`} gap={`5`}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`column`} gap={`1`}>
  <RadixThemesBox css={{"as": "button", "underline": "none", "weight": "medium", "width": "100%"}} onClick={toggleColorMode}>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"&:hover": {"cursor": "pointer", "background": "var(--accent-4)", "color": "var(--accent-11)"}, "color": "var(--accent-11)", "border-radius": "0.5em", "width": "100%", "paddingInlineStart": "0.5rem", "paddingInlineEnd": "0.5rem", "paddingTop": "0.75rem", "paddingBottom": "0.75rem"}} direction={`row`} gap={`3`}>
  <Fragment>
  {isTrue(((colorMode) === (`light`))) ? (
  <Fragment>
  <LucideMoonIcon css={{"color": "var(--current-color)"}}/>
</Fragment>
) : (
  <Fragment>
  <LucideSunIcon css={{"color": "var(--current-color)"}}/>
</Fragment>
)}
</Fragment>
  <RadixThemesText as={`p`} size={`4`}>
  {isTrue(((colorMode) === (`light`))) ? `Turn dark mode on` : `Turn light mode on`}
</RadixThemesText>
</RadixThemesFlex>
</RadixThemesBox>
  <RadixThemesBox css={{"as": "button", "underline": "none", "weight": "medium", "width": "100%"}} onClick={(_e) => addEvents([Event("state.nav_state.to_logout", {})], (_e), {})}>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"&:hover": {"cursor": "pointer", "background": "var(--accent-4)", "color": "var(--accent-11)"}, "color": "var(--accent-11)", "border-radius": "0.5em", "width": "100%", "paddingInlineStart": "0.5rem", "paddingInlineEnd": "0.5rem", "paddingTop": "0.75rem", "paddingBottom": "0.75rem"}} direction={`row`} gap={`3`}>
  <LucideLogOutIcon css={{"color": "var(--current-color)"}}/>
  <RadixThemesText as={`p`} size={`4`}>
  {`Logout`}
</RadixThemesText>
</RadixThemesFlex>
</RadixThemesBox>
</RadixThemesFlex>
  <RadixThemesSeparator size={`4`}/>
  <Fragment>
  {isTrue(state__local_auth_state__session_state.authenticated_user_info) ? (
  <Fragment>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"paddingInlineStart": "0.5rem", "paddingInlineEnd": "0.5rem", "width": "100%"}} direction={`row`} justify={`start`} gap={`3`}>
  <RadixThemesIconButton css={{"padding": "6px"}} radius={`full`} size={`3`}>
  <LucideUserIcon css={{"color": "var(--current-color)"}} size={36}/>
</RadixThemesIconButton>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`column`} justify={`start`} gap={`0`}>
  <RadixThemesBox css={{"width": "100%"}}>
  <RadixThemesText as={`p`} size={`3`} weight={`bold`}>
  {isTrue(state__local_auth_state__session_state.authenticated_username) ? state__local_auth_state__session_state.authenticated_username : `Account`}
</RadixThemesText>
  <RadixThemesText as={`p`} size={`2`} weight={`medium`}>
  {`${state__local_auth_state__session_state.authenticated_user_info?.email}`}
</RadixThemesText>
</RadixThemesBox>
</RadixThemesFlex>
</RadixThemesFlex>
</Fragment>
) : (
  <Fragment>
  {``}
</Fragment>
)}
</Fragment>
</RadixThemesFlex>
</RadixThemesFlex>
</RadixThemesBox>
  <RadixThemesBox css={{"padding": "1em", "@media screen and (min-width: 0)": {"display": "block"}, "@media screen and (min-width: 30em)": {"display": "block"}, "@media screen and (min-width: 48em)": {"display": "block"}, "@media screen and (min-width: 62em)": {"display": "none"}}}>
  <VaulDrawer.Root direction={`left`}>
  <VaulDrawer.Trigger asChild={true}>
  <LucideAlignJustifyIcon css={{"color": "var(--current-color)"}} size={30}/>
</VaulDrawer.Trigger>
  <VaulDrawer.Overlay css={{"position": "fixed", "left": "0", "right": "0", "bottom": "0", "top": "0", "z_index": 50, "background": "rgba(0, 0, 0, 0.5)", "zIndex": "5"}}/>
  <VaulDrawer.Portal css={{"width": "100%"}}>
  <RadixThemesTheme css={{...theme.styles.global[':root'], ...theme.styles.global.body}}>
  <VaulDrawer.Content css={{"left": "0", "right": "auto", "bottom": "0", "top": "auto", "position": "fixed", "z_index": 50, "display": "flex", "height": "100%", "width": "20em", "padding": "1.5em", "background": "var(--accent-2)"}}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`column`} gap={`5`}>
  <RadixThemesBox css={{"width": "100%"}}>
  <VaulDrawer.Close asChild={true}>
  <LucideXIcon css={{"color": "var(--current-color)"}} size={30}/>
</VaulDrawer.Close>
</RadixThemesBox>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`column`} gap={`1`}>
  <RadixThemesLink asChild={true} css={{"width": "100%", "&:hover": {"color": "var(--accent-8)"}}} underline={`none`} weight={`medium`}>
  <NextLink href={`/`} passHref={true}>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"&:hover": {"background": "var(--accent-4)", "color": "var(--accent-11)"}, "border-radius": "0.5em", "width": "100%", "paddingInlineStart": "0.5rem", "paddingInlineEnd": "0.5rem", "paddingTop": "0.75rem", "paddingBottom": "0.75rem"}} direction={`row`} gap={`3`}>
  <LucideLayoutDashboardIcon css={{"color": "var(--current-color)"}}/>
  <RadixThemesText as={`p`} size={`4`}>
  {`Dashboard`}
</RadixThemesText>
</RadixThemesFlex>
</NextLink>
</RadixThemesLink>
  <RadixThemesLink asChild={true} css={{"width": "100%", "&:hover": {"color": "var(--accent-8)"}}} underline={`none`} weight={`medium`}>
  <NextLink href={`/articles`} passHref={true}>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"&:hover": {"background": "var(--accent-4)", "color": "var(--accent-11)"}, "border-radius": "0.5em", "width": "100%", "paddingInlineStart": "0.5rem", "paddingInlineEnd": "0.5rem", "paddingTop": "0.75rem", "paddingBottom": "0.75rem"}} direction={`row`} gap={`3`}>
  <LucideGlobeIcon css={{"color": "var(--current-color)"}}/>
  <RadixThemesText as={`p`} size={`4`}>
  {`Articles`}
</RadixThemesText>
</RadixThemesFlex>
</NextLink>
</RadixThemesLink>
  <RadixThemesLink asChild={true} css={{"width": "100%", "&:hover": {"color": "var(--accent-8)"}}} underline={`none`} weight={`medium`}>
  <NextLink href={`/blog`} passHref={true}>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"&:hover": {"background": "var(--accent-4)", "color": "var(--accent-11)"}, "border-radius": "0.5em", "width": "100%", "paddingInlineStart": "0.5rem", "paddingInlineEnd": "0.5rem", "paddingTop": "0.75rem", "paddingBottom": "0.75rem"}} direction={`row`} gap={`3`}>
  <LucideNewspaperIcon css={{"color": "var(--current-color)"}}/>
  <RadixThemesText as={`p`} size={`4`}>
  {`Blog`}
</RadixThemesText>
</RadixThemesFlex>
</NextLink>
</RadixThemesLink>
  <RadixThemesLink asChild={true} css={{"width": "100%", "&:hover": {"color": "var(--accent-8)"}}} underline={`none`} weight={`medium`}>
  <NextLink href={`/blog/add`} passHref={true}>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"&:hover": {"background": "var(--accent-4)", "color": "var(--accent-11)"}, "border-radius": "0.5em", "width": "100%", "paddingInlineStart": "0.5rem", "paddingInlineEnd": "0.5rem", "paddingTop": "0.75rem", "paddingBottom": "0.75rem"}} direction={`row`} gap={`3`}>
  <LucideSquareLibraryIcon css={{"color": "var(--current-color)"}}/>
  <RadixThemesText as={`p`} size={`4`}>
  {`Create post`}
</RadixThemesText>
</RadixThemesFlex>
</NextLink>
</RadixThemesLink>
  <RadixThemesLink asChild={true} css={{"width": "100%", "&:hover": {"color": "var(--accent-8)"}}} underline={`none`} weight={`medium`}>
  <NextLink href={`/contact`} passHref={true}>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"&:hover": {"background": "var(--accent-4)", "color": "var(--accent-11)"}, "border-radius": "0.5em", "width": "100%", "paddingInlineStart": "0.5rem", "paddingInlineEnd": "0.5rem", "paddingTop": "0.75rem", "paddingBottom": "0.75rem"}} direction={`row`} gap={`3`}>
  <LucideMailIcon css={{"color": "var(--current-color)"}}/>
  <RadixThemesText as={`p`} size={`4`}>
  {`Contact`}
</RadixThemesText>
</RadixThemesFlex>
</NextLink>
</RadixThemesLink>
  <RadixThemesLink asChild={true} css={{"width": "100%", "&:hover": {"color": "var(--accent-8)"}}} underline={`none`} weight={`medium`}>
  <NextLink href={`/contact/entries`} passHref={true}>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"&:hover": {"background": "var(--accent-4)", "color": "var(--accent-11)"}, "border-radius": "0.5em", "width": "100%", "paddingInlineStart": "0.5rem", "paddingInlineEnd": "0.5rem", "paddingTop": "0.75rem", "paddingBottom": "0.75rem"}} direction={`row`} gap={`3`}>
  <LucideMailboxIcon css={{"color": "var(--current-color)"}}/>
  <RadixThemesText as={`p`} size={`4`}>
  {`Contact History`}
</RadixThemesText>
</RadixThemesFlex>
</NextLink>
</RadixThemesLink>
</RadixThemesFlex>
  <RadixThemesFlex css={{"flex": 1, "justifySelf": "stretch", "alignSelf": "stretch"}}/>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`column`} gap={`5`}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`column`} gap={`1`}>
  <RadixThemesBox css={{"as": "button", "underline": "none", "weight": "medium", "width": "100%"}} onClick={toggleColorMode}>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"&:hover": {"cursor": "pointer", "background": "var(--accent-4)", "color": "var(--accent-11)"}, "color": "var(--accent-11)", "border-radius": "0.5em", "width": "100%", "paddingInlineStart": "0.5rem", "paddingInlineEnd": "0.5rem", "paddingTop": "0.75rem", "paddingBottom": "0.75rem"}} direction={`row`} gap={`3`}>
  <Fragment>
  {isTrue(((colorMode) === (`light`))) ? (
  <Fragment>
  <LucideMoonIcon css={{"color": "var(--current-color)"}}/>
</Fragment>
) : (
  <Fragment>
  <LucideSunIcon css={{"color": "var(--current-color)"}}/>
</Fragment>
)}
</Fragment>
  <RadixThemesText as={`p`} size={`4`}>
  {isTrue(((colorMode) === (`light`))) ? `Turn dark mode on` : `Turn light mode on`}
</RadixThemesText>
</RadixThemesFlex>
</RadixThemesBox>
  <RadixThemesBox css={{"as": "button", "underline": "none", "weight": "medium", "width": "100%"}} onClick={(_e) => addEvents([Event("state.nav_state.to_logout", {})], (_e), {})}>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"&:hover": {"cursor": "pointer", "background": "var(--accent-4)", "color": "var(--accent-11)"}, "color": "var(--accent-11)", "border-radius": "0.5em", "width": "100%", "paddingInlineStart": "0.5rem", "paddingInlineEnd": "0.5rem", "paddingTop": "0.75rem", "paddingBottom": "0.75rem"}} direction={`row`} gap={`3`}>
  <LucideLogOutIcon css={{"color": "var(--current-color)"}}/>
  <RadixThemesText as={`p`} size={`4`}>
  {`Logout`}
</RadixThemesText>
</RadixThemesFlex>
</RadixThemesBox>
</RadixThemesFlex>
  <RadixThemesSeparator css={{"margin": "0"}} size={`4`}/>
  <Fragment>
  {isTrue(state__local_auth_state__session_state.authenticated_user_info) ? (
  <Fragment>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"paddingInlineStart": "0.5rem", "paddingInlineEnd": "0.5rem", "width": "100%"}} direction={`row`} justify={`start`} gap={`3`}>
  <RadixThemesIconButton css={{"padding": "6px"}} radius={`full`} size={`3`}>
  <LucideUserIcon css={{"color": "var(--current-color)"}} size={36}/>
</RadixThemesIconButton>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`column`} justify={`start`} gap={`0`}>
  <RadixThemesBox css={{"width": "100%"}}>
  <RadixThemesText as={`p`} size={`3`} weight={`bold`}>
  {isTrue(state__local_auth_state__session_state.authenticated_username) ? state__local_auth_state__session_state.authenticated_username : `Account`}
</RadixThemesText>
  <RadixThemesText as={`p`} size={`2`} weight={`medium`}>
  {`${state__local_auth_state__session_state.authenticated_user_info?.email}`}
</RadixThemesText>
</RadixThemesBox>
</RadixThemesFlex>
</RadixThemesFlex>
</Fragment>
) : (
  <Fragment>
  {``}
</Fragment>
)}
</Fragment>
</RadixThemesFlex>
</RadixThemesFlex>
</VaulDrawer.Content>
</RadixThemesTheme>
</VaulDrawer.Portal>
</VaulDrawer.Root>
</RadixThemesBox>
</RadixThemesBox>
  <RadixThemesBox css={{"padding": "1em", "width": "100%"}} id={`my-content-area-el`} ref={ref_my_content_area_el}>
  <Fragment>
  {isTrue(state__local_auth_state__session_state__blog_post_state.post) ? (
  <Fragment>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"minHeight": "95vh"}} direction={`column`} gap={`5`}>
  <RadixThemesHeading size={`9`}>
  {`Editing `}
  {state__local_auth_state__session_state__blog_post_state.post?.title}
</RadixThemesHeading>
  <RadixThemesBox css={{"@media screen and (min-width: 0)": {"display": "none"}, "@media screen and (min-width: 30em)": {"display": "none"}, "@media screen and (min-width: 48em)": {"display": "none"}, "@media screen and (min-width: 62em)": {"display": "block"}}}>
  <RadixThemesBox css={{"width": "50vw"}}>
  <RadixFormRoot className={`Root`} css={{"width": "100%"}} onSubmit={handleSubmit_54e581d5da48387adcf7cd9a2b15226c}>
  <RadixThemesBox css={{"display": "none"}}>
  <RadixThemesTextField.Root name={`post_id`} type={`hidden`} value={state__local_auth_state__session_state__blog_post_state.post?.id}/>
</RadixThemesBox>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} direction={`column`} gap={`3`}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`row`} gap={`3`}>
  <RadixThemesTextField.Root css={{"width": "100%"}} defaultValue={state__local_auth_state__session_state__blog_post_state.post?.title} name={`title`} placeholder={`Title`} required={true} type={`text`}/>
</RadixThemesFlex>
  <DebounceInput css={{"height": "50vh", "width": "100%"}} debounceTimeout={300} element={RadixThemesTextArea} name={`content`} onChange={(_e0) => addEvents([Event("state.local_auth_state.session_state.blog_post_state.set_post_content", {value:_e0.target.value})], (_e0), {})} placeholder={`Your message`} required={true} value={state__local_auth_state__session_state__blog_post_state.post_content}/>
  <RadixThemesFlex gap={`2`}>
  <RadixThemesSwitch defaultChecked={state__local_auth_state__session_state__blog_post_state.post_publish_active} name={`publish_active`} onCheckedChange={(_checked) => addEvents([Event("state.local_auth_state.session_state.blog_post_state.set_post_publish_active", {value:_checked})], (_checked), {})}/>
  <RadixThemesText as={`p`}>
  {`Publish Active`}
</RadixThemesText>
</RadixThemesFlex>
  <Fragment>
  {isTrue(state__local_auth_state__session_state__blog_post_state.post_publish_active) ? (
  <Fragment>
  <RadixThemesBox css={{"width": "100%"}}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`row`} gap={`3`}>
  <RadixThemesTextField.Root css={{"width": "100%"}} defaultValue={state__local_auth_state__session_state__blog_post_state__blog_edit_form_state.publish_display_date} name={`publish_date`} type={`date`}/>
  <RadixThemesTextField.Root css={{"width": "100%"}} defaultValue={state__local_auth_state__session_state__blog_post_state__blog_edit_form_state.publish_display_time} name={`publish_time`} type={`time`}/>
</RadixThemesFlex>
</RadixThemesBox>
</Fragment>
) : (
  <Fragment/>
)}
</Fragment>
  <RadixThemesButton type={`submit`}>
  {`Submit`}
</RadixThemesButton>
</RadixThemesFlex>
</RadixFormRoot>
</RadixThemesBox>
</RadixThemesBox>
  <RadixThemesBox css={{"@media screen and (min-width: 0)": {"display": "none"}, "@media screen and (min-width: 30em)": {"display": "block"}, "@media screen and (min-width: 48em)": {"display": "block"}, "@media screen and (min-width: 62em)": {"display": "none"}}}>
  <RadixThemesBox css={{"width": "75vw"}}>
  <RadixFormRoot className={`Root`} css={{"width": "100%"}} onSubmit={handleSubmit_54e581d5da48387adcf7cd9a2b15226c}>
  <RadixThemesBox css={{"display": "none"}}>
  <RadixThemesTextField.Root name={`post_id`} type={`hidden`} value={state__local_auth_state__session_state__blog_post_state.post?.id}/>
</RadixThemesBox>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} direction={`column`} gap={`3`}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`row`} gap={`3`}>
  <RadixThemesTextField.Root css={{"width": "100%"}} defaultValue={state__local_auth_state__session_state__blog_post_state.post?.title} name={`title`} placeholder={`Title`} required={true} type={`text`}/>
</RadixThemesFlex>
  <DebounceInput css={{"height": "50vh", "width": "100%"}} debounceTimeout={300} element={RadixThemesTextArea} name={`content`} onChange={(_e0) => addEvents([Event("state.local_auth_state.session_state.blog_post_state.set_post_content", {value:_e0.target.value})], (_e0), {})} placeholder={`Your message`} required={true} value={state__local_auth_state__session_state__blog_post_state.post_content}/>
  <RadixThemesFlex gap={`2`}>
  <RadixThemesSwitch defaultChecked={state__local_auth_state__session_state__blog_post_state.post_publish_active} name={`publish_active`} onCheckedChange={(_checked) => addEvents([Event("state.local_auth_state.session_state.blog_post_state.set_post_publish_active", {value:_checked})], (_checked), {})}/>
  <RadixThemesText as={`p`}>
  {`Publish Active`}
</RadixThemesText>
</RadixThemesFlex>
  <Fragment>
  {isTrue(state__local_auth_state__session_state__blog_post_state.post_publish_active) ? (
  <Fragment>
  <RadixThemesBox css={{"width": "100%"}}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`row`} gap={`3`}>
  <RadixThemesTextField.Root css={{"width": "100%"}} defaultValue={state__local_auth_state__session_state__blog_post_state__blog_edit_form_state.publish_display_date} name={`publish_date`} type={`date`}/>
  <RadixThemesTextField.Root css={{"width": "100%"}} defaultValue={state__local_auth_state__session_state__blog_post_state__blog_edit_form_state.publish_display_time} name={`publish_time`} type={`time`}/>
</RadixThemesFlex>
</RadixThemesBox>
</Fragment>
) : (
  <Fragment/>
)}
</Fragment>
  <RadixThemesButton type={`submit`}>
  {`Submit`}
</RadixThemesButton>
</RadixThemesFlex>
</RadixFormRoot>
</RadixThemesBox>
</RadixThemesBox>
  <RadixThemesBox css={{"@media screen and (min-width: 0)": {"display": "block"}, "@media screen and (min-width: 30em)": {"display": "none"}, "@media screen and (min-width: 48em)": {"display": "none"}, "@media screen and (min-width: 62em)": {"display": "none"}}}>
  <RadixThemesBox css={{"width": "85vw"}} id={`my-form-box`} ref={ref_my_form_box}>
  <RadixFormRoot className={`Root`} css={{"width": "100%"}} onSubmit={handleSubmit_54e581d5da48387adcf7cd9a2b15226c}>
  <RadixThemesBox css={{"display": "none"}}>
  <RadixThemesTextField.Root name={`post_id`} type={`hidden`} value={state__local_auth_state__session_state__blog_post_state.post?.id}/>
</RadixThemesBox>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} direction={`column`} gap={`3`}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`row`} gap={`3`}>
  <RadixThemesTextField.Root css={{"width": "100%"}} defaultValue={state__local_auth_state__session_state__blog_post_state.post?.title} name={`title`} placeholder={`Title`} required={true} type={`text`}/>
</RadixThemesFlex>
  <DebounceInput css={{"height": "50vh", "width": "100%"}} debounceTimeout={300} element={RadixThemesTextArea} name={`content`} onChange={(_e0) => addEvents([Event("state.local_auth_state.session_state.blog_post_state.set_post_content", {value:_e0.target.value})], (_e0), {})} placeholder={`Your message`} required={true} value={state__local_auth_state__session_state__blog_post_state.post_content}/>
  <RadixThemesFlex gap={`2`}>
  <RadixThemesSwitch defaultChecked={state__local_auth_state__session_state__blog_post_state.post_publish_active} name={`publish_active`} onCheckedChange={(_checked) => addEvents([Event("state.local_auth_state.session_state.blog_post_state.set_post_publish_active", {value:_checked})], (_checked), {})}/>
  <RadixThemesText as={`p`}>
  {`Publish Active`}
</RadixThemesText>
</RadixThemesFlex>
  <Fragment>
  {isTrue(state__local_auth_state__session_state__blog_post_state.post_publish_active) ? (
  <Fragment>
  <RadixThemesBox css={{"width": "100%"}}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`row`} gap={`3`}>
  <RadixThemesTextField.Root css={{"width": "100%"}} defaultValue={state__local_auth_state__session_state__blog_post_state__blog_edit_form_state.publish_display_date} name={`publish_date`} type={`date`}/>
  <RadixThemesTextField.Root css={{"width": "100%"}} defaultValue={state__local_auth_state__session_state__blog_post_state__blog_edit_form_state.publish_display_time} name={`publish_time`} type={`time`}/>
</RadixThemesFlex>
</RadixThemesBox>
</Fragment>
) : (
  <Fragment/>
)}
</Fragment>
  <RadixThemesButton type={`submit`}>
  {`Submit`}
</RadixThemesButton>
</RadixThemesFlex>
</RadixFormRoot>
</RadixThemesBox>
</RadixThemesBox>
</RadixThemesFlex>
</Fragment>
) : (
  <Fragment>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"minHeight": "85vh"}} direction={`row`} gap={`5`}>
  <RadixThemesHeading>
  {`Blog PostNot Found`}
</RadixThemesHeading>
</RadixThemesFlex>
</Fragment>
)}
</Fragment>
  <RadixThemesFlex css={{"display": "flex", "alignItems": "center", "justifyContent": "center", "width": "100%"}}>
  <RadixThemesLink asChild={true} css={{"&:hover": {"color": "var(--accent-8)"}}} size={`3`}>
  <NextLink href={`https://reflex.dev`} passHref={true}>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"textAlign": "center", "padding": "1em"}} direction={`row`} gap={`3`}>
  {`Built with `}
  <Fragment>
  {isTrue(((colorMode) === (`light`))) ? (
  <Fragment>
  <div className={`rx-Html`} dangerouslySetInnerHTML={{"__html": "<svg width=\"56\" height=\"12\" viewBox=\"0 0 56 12\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\">\n<path d=\"M0 11.6V0.400024H8.96V4.88002H6.72V2.64002H2.24V4.88002H6.72V7.12002H2.24V11.6H0ZM6.72 11.6V7.12002H8.96V11.6H6.72Z\" fill=\"#110F1F\"/>\n<path d=\"M11.2 11.6V0.400024H17.92V2.64002H13.44V4.88002H17.92V7.12002H13.44V9.36002H17.92V11.6H11.2Z\" fill=\"#110F1F\"/>\n<path d=\"M20.16 11.6V0.400024H26.88V2.64002H22.4V4.88002H26.88V7.12002H22.4V11.6H20.16Z\" fill=\"#110F1F\"/>\n<path d=\"M29.12 11.6V0.400024H31.36V9.36002H35.84V11.6H29.12Z\" fill=\"#110F1F\"/>\n<path d=\"M38.08 11.6V0.400024H44.8V2.64002H40.32V4.88002H44.8V7.12002H40.32V9.36002H44.8V11.6H38.08Z\" fill=\"#110F1F\"/>\n<path d=\"M47.04 4.88002V0.400024H49.28V4.88002H47.04ZM53.76 4.88002V0.400024H56V4.88002H53.76ZM49.28 7.12002V4.88002H53.76V7.12002H49.28ZM47.04 11.6V7.12002H49.28V11.6H47.04ZM53.76 11.6V7.12002H56V11.6H53.76Z\" fill=\"#110F1F\"/>\n</svg>"}}/>
</Fragment>
) : (
  <Fragment>
  <div className={`rx-Html`} dangerouslySetInnerHTML={{"__html": "<svg width=\"56\" height=\"12\" viewBox=\"0 0 56 12\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\">\n<path d=\"M0 11.5999V0.399902H8.96V4.8799H6.72V2.6399H2.24V4.8799H6.72V7.1199H2.24V11.5999H0ZM6.72 11.5999V7.1199H8.96V11.5999H6.72Z\" fill=\"white\"/>\n<path d=\"M11.2 11.5999V0.399902H17.92V2.6399H13.44V4.8799H17.92V7.1199H13.44V9.3599H17.92V11.5999H11.2Z\" fill=\"white\"/>\n<path d=\"M20.16 11.5999V0.399902H26.88V2.6399H22.4V4.8799H26.88V7.1199H22.4V11.5999H20.16Z\" fill=\"white\"/>\n<path d=\"M29.12 11.5999V0.399902H31.36V9.3599H35.84V11.5999H29.12Z\" fill=\"white\"/>\n<path d=\"M38.08 11.5999V0.399902H44.8V2.6399H40.32V4.8799H44.8V7.1199H40.32V9.3599H44.8V11.5999H38.08Z\" fill=\"white\"/>\n<path d=\"M47.04 4.8799V0.399902H49.28V4.8799H47.04ZM53.76 4.8799V0.399902H56V4.8799H53.76ZM49.28 7.1199V4.8799H53.76V7.1199H49.28ZM47.04 11.5999V7.1199H49.28V11.5999H47.04ZM53.76 11.5999V7.1199H56V11.5999H53.76Z\" fill=\"white\"/>\n</svg>"}}/>
</Fragment>
)}
</Fragment>
</RadixThemesFlex>
</NextLink>
</RadixThemesLink>
</RadixThemesFlex>
</RadixThemesBox>
</RadixThemesFlex>
</Fragment>
) : (
  <Fragment>
  <RadixThemesBox css={{"background": "var(--accent-3)", "padding": "1em", "width": "100%"}} id={`my-main-nav`} ref={ref_my_main_nav}>
  <RadixThemesBox css={{"@media screen and (min-width: 0)": {"display": "none"}, "@media screen and (min-width: 30em)": {"display": "none"}, "@media screen and (min-width: 48em)": {"display": "none"}, "@media screen and (min-width: 62em)": {"display": "block"}}}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"alignItems": "center"}} direction={`row`} id={`my-navbar-hstack-desktop`} justify={`between`} ref={ref_my_navbar_hstack_desktop} gap={`3`}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"alignItems": "center"}} direction={`row`} gap={`3`}>
  <RadixThemesLink asChild={true} css={{"&:hover": {"color": "var(--accent-8)"}}}>
  <NextLink href={`/`} passHref={true}>
  <img css={{"width": "2.25em", "height": "auto", "borderRadius": "25%"}} src={`/logo.jpg`}/>
</NextLink>
</RadixThemesLink>
  <RadixThemesLink asChild={true} css={{"&:hover": {"color": "var(--accent-8)"}}}>
  <NextLink href={`/`} passHref={true}>
  <RadixThemesHeading size={`7`} weight={`bold`}>
  {`Reflex`}
</RadixThemesHeading>
</NextLink>
</RadixThemesLink>
</RadixThemesFlex>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} direction={`row`} gap={`5`}>
  <RadixThemesLink asChild={true} css={{"&:hover": {"color": "var(--accent-8)"}}}>
  <NextLink href={`/`} passHref={true}>
  <RadixThemesText as={`p`} size={`4`} weight={`medium`}>
  {`Home`}
</RadixThemesText>
</NextLink>
</RadixThemesLink>
  <RadixThemesLink asChild={true} css={{"&:hover": {"color": "var(--accent-8)"}}}>
  <NextLink href={`/about`} passHref={true}>
  <RadixThemesText as={`p`} size={`4`} weight={`medium`}>
  {`About`}
</RadixThemesText>
</NextLink>
</RadixThemesLink>
  <RadixThemesLink asChild={true} css={{"&:hover": {"color": "var(--accent-8)"}}}>
  <NextLink href={`/articles`} passHref={true}>
  <RadixThemesText as={`p`} size={`4`} weight={`medium`}>
  {`Articles`}
</RadixThemesText>
</NextLink>
</RadixThemesLink>
  <RadixThemesLink asChild={true} css={{"&:hover": {"color": "var(--accent-8)"}}}>
  <NextLink href={`/pricing`} passHref={true}>
  <RadixThemesText as={`p`} size={`4`} weight={`medium`}>
  {`Pricing`}
</RadixThemesText>
</NextLink>
</RadixThemesLink>
  <RadixThemesLink asChild={true} css={{"&:hover": {"color": "var(--accent-8)"}}}>
  <NextLink href={`/contact`} passHref={true}>
  <RadixThemesText as={`p`} size={`4`} weight={`medium`}>
  {`Contact`}
</RadixThemesText>
</NextLink>
</RadixThemesLink>
</RadixThemesFlex>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} direction={`row`} justify={`end`} gap={`4`}>
  <RadixThemesLink asChild={true} css={{"&:hover": {"color": "var(--accent-8)"}}}>
  <NextLink href={`/register`} passHref={true}>
  <RadixThemesButton size={`3`} variant={`outline`}>
  {`Register`}
</RadixThemesButton>
</NextLink>
</RadixThemesLink>
  <RadixThemesLink asChild={true} css={{"&:hover": {"color": "var(--accent-8)"}}}>
  <NextLink href={`/login`} passHref={true}>
  <RadixThemesButton size={`3`} variant={`outline`}>
  {`Login`}
</RadixThemesButton>
</NextLink>
</RadixThemesLink>
</RadixThemesFlex>
</RadixThemesFlex>
</RadixThemesBox>
  <RadixThemesBox css={{"@media screen and (min-width: 0)": {"display": "block"}, "@media screen and (min-width: 30em)": {"display": "block"}, "@media screen and (min-width: 48em)": {"display": "block"}, "@media screen and (min-width: 62em)": {"display": "none"}}}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"alignItems": "center"}} direction={`row`} justify={`between`} gap={`3`}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"alignItems": "center"}} direction={`row`} gap={`3`}>
  <img css={{"width": "2em", "height": "auto", "borderRadius": "25%"}} src={`/logo.jpg`}/>
  <RadixThemesHeading size={`6`} weight={`bold`}>
  {`Reflex`}
</RadixThemesHeading>
</RadixThemesFlex>
  <RadixThemesDropdownMenu.Root css={{"justify": "end"}}>
  <RadixThemesDropdownMenu.Trigger>
  <LucideMenuIcon css={{"color": "var(--current-color)"}} size={30}/>
</RadixThemesDropdownMenu.Trigger>
  <RadixThemesDropdownMenu.Content>
  <RadixThemesDropdownMenu.Item onClick={(_e) => addEvents([Event("state.nav_state.to_home", {})], (_e), {})}>
  {`Home`}
</RadixThemesDropdownMenu.Item>
  <RadixThemesDropdownMenu.Item onClick={(_e) => addEvents([Event("state.nav_state.to_articles", {})], (_e), {})}>
  {`Articles`}
</RadixThemesDropdownMenu.Item>
  <RadixThemesDropdownMenu.Item onClick={(_e) => addEvents([Event("state.nav_state.to_blog", {})], (_e), {})}>
  {`Blog`}
</RadixThemesDropdownMenu.Item>
  <RadixThemesDropdownMenu.Item onClick={(_e) => addEvents([Event("state.nav_state.to_pricing", {})], (_e), {})}>
  {`Pricing`}
</RadixThemesDropdownMenu.Item>
  <RadixThemesDropdownMenu.Item onClick={(_e) => addEvents([Event("state.nav_state.to_contact", {})], (_e), {})}>
  {`Contact`}
</RadixThemesDropdownMenu.Item>
  <RadixThemesDropdownMenu.Separator/>
  <RadixThemesDropdownMenu.Item onClick={(_e) => addEvents([Event("state.nav_state.to_login", {})], (_e), {})}>
  {`Log in`}
</RadixThemesDropdownMenu.Item>
  <RadixThemesDropdownMenu.Item onClick={(_e) => addEvents([Event("state.nav_state.to_register", {})], (_e), {})}>
  {`Register`}
</RadixThemesDropdownMenu.Item>
</RadixThemesDropdownMenu.Content>
</RadixThemesDropdownMenu.Root>
</RadixThemesFlex>
</RadixThemesBox>
</RadixThemesBox>
  <RadixThemesBox css={{"padding": "1em", "width": "100%"}} id={`my-content-area-el`} ref={ref_my_content_area_el}>
  <Fragment>
  {isTrue(state__local_auth_state__session_state__blog_post_state.post) ? (
  <Fragment>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"minHeight": "95vh"}} direction={`column`} gap={`5`}>
  <RadixThemesHeading size={`9`}>
  {`Editing `}
  {state__local_auth_state__session_state__blog_post_state.post?.title}
</RadixThemesHeading>
  <RadixThemesBox css={{"@media screen and (min-width: 0)": {"display": "none"}, "@media screen and (min-width: 30em)": {"display": "none"}, "@media screen and (min-width: 48em)": {"display": "none"}, "@media screen and (min-width: 62em)": {"display": "block"}}}>
  <RadixThemesBox css={{"width": "50vw"}}>
  <RadixFormRoot className={`Root`} css={{"width": "100%"}} onSubmit={handleSubmit_54e581d5da48387adcf7cd9a2b15226c}>
  <RadixThemesBox css={{"display": "none"}}>
  <RadixThemesTextField.Root name={`post_id`} type={`hidden`} value={state__local_auth_state__session_state__blog_post_state.post?.id}/>
</RadixThemesBox>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} direction={`column`} gap={`3`}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`row`} gap={`3`}>
  <RadixThemesTextField.Root css={{"width": "100%"}} defaultValue={state__local_auth_state__session_state__blog_post_state.post?.title} name={`title`} placeholder={`Title`} required={true} type={`text`}/>
</RadixThemesFlex>
  <DebounceInput css={{"height": "50vh", "width": "100%"}} debounceTimeout={300} element={RadixThemesTextArea} name={`content`} onChange={(_e0) => addEvents([Event("state.local_auth_state.session_state.blog_post_state.set_post_content", {value:_e0.target.value})], (_e0), {})} placeholder={`Your message`} required={true} value={state__local_auth_state__session_state__blog_post_state.post_content}/>
  <RadixThemesFlex gap={`2`}>
  <RadixThemesSwitch defaultChecked={state__local_auth_state__session_state__blog_post_state.post_publish_active} name={`publish_active`} onCheckedChange={(_checked) => addEvents([Event("state.local_auth_state.session_state.blog_post_state.set_post_publish_active", {value:_checked})], (_checked), {})}/>
  <RadixThemesText as={`p`}>
  {`Publish Active`}
</RadixThemesText>
</RadixThemesFlex>
  <Fragment>
  {isTrue(state__local_auth_state__session_state__blog_post_state.post_publish_active) ? (
  <Fragment>
  <RadixThemesBox css={{"width": "100%"}}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`row`} gap={`3`}>
  <RadixThemesTextField.Root css={{"width": "100%"}} defaultValue={state__local_auth_state__session_state__blog_post_state__blog_edit_form_state.publish_display_date} name={`publish_date`} type={`date`}/>
  <RadixThemesTextField.Root css={{"width": "100%"}} defaultValue={state__local_auth_state__session_state__blog_post_state__blog_edit_form_state.publish_display_time} name={`publish_time`} type={`time`}/>
</RadixThemesFlex>
</RadixThemesBox>
</Fragment>
) : (
  <Fragment/>
)}
</Fragment>
  <RadixThemesButton type={`submit`}>
  {`Submit`}
</RadixThemesButton>
</RadixThemesFlex>
</RadixFormRoot>
</RadixThemesBox>
</RadixThemesBox>
  <RadixThemesBox css={{"@media screen and (min-width: 0)": {"display": "none"}, "@media screen and (min-width: 30em)": {"display": "block"}, "@media screen and (min-width: 48em)": {"display": "block"}, "@media screen and (min-width: 62em)": {"display": "none"}}}>
  <RadixThemesBox css={{"width": "75vw"}}>
  <RadixFormRoot className={`Root`} css={{"width": "100%"}} onSubmit={handleSubmit_54e581d5da48387adcf7cd9a2b15226c}>
  <RadixThemesBox css={{"display": "none"}}>
  <RadixThemesTextField.Root name={`post_id`} type={`hidden`} value={state__local_auth_state__session_state__blog_post_state.post?.id}/>
</RadixThemesBox>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} direction={`column`} gap={`3`}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`row`} gap={`3`}>
  <RadixThemesTextField.Root css={{"width": "100%"}} defaultValue={state__local_auth_state__session_state__blog_post_state.post?.title} name={`title`} placeholder={`Title`} required={true} type={`text`}/>
</RadixThemesFlex>
  <DebounceInput css={{"height": "50vh", "width": "100%"}} debounceTimeout={300} element={RadixThemesTextArea} name={`content`} onChange={(_e0) => addEvents([Event("state.local_auth_state.session_state.blog_post_state.set_post_content", {value:_e0.target.value})], (_e0), {})} placeholder={`Your message`} required={true} value={state__local_auth_state__session_state__blog_post_state.post_content}/>
  <RadixThemesFlex gap={`2`}>
  <RadixThemesSwitch defaultChecked={state__local_auth_state__session_state__blog_post_state.post_publish_active} name={`publish_active`} onCheckedChange={(_checked) => addEvents([Event("state.local_auth_state.session_state.blog_post_state.set_post_publish_active", {value:_checked})], (_checked), {})}/>
  <RadixThemesText as={`p`}>
  {`Publish Active`}
</RadixThemesText>
</RadixThemesFlex>
  <Fragment>
  {isTrue(state__local_auth_state__session_state__blog_post_state.post_publish_active) ? (
  <Fragment>
  <RadixThemesBox css={{"width": "100%"}}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`row`} gap={`3`}>
  <RadixThemesTextField.Root css={{"width": "100%"}} defaultValue={state__local_auth_state__session_state__blog_post_state__blog_edit_form_state.publish_display_date} name={`publish_date`} type={`date`}/>
  <RadixThemesTextField.Root css={{"width": "100%"}} defaultValue={state__local_auth_state__session_state__blog_post_state__blog_edit_form_state.publish_display_time} name={`publish_time`} type={`time`}/>
</RadixThemesFlex>
</RadixThemesBox>
</Fragment>
) : (
  <Fragment/>
)}
</Fragment>
  <RadixThemesButton type={`submit`}>
  {`Submit`}
</RadixThemesButton>
</RadixThemesFlex>
</RadixFormRoot>
</RadixThemesBox>
</RadixThemesBox>
  <RadixThemesBox css={{"@media screen and (min-width: 0)": {"display": "block"}, "@media screen and (min-width: 30em)": {"display": "none"}, "@media screen and (min-width: 48em)": {"display": "none"}, "@media screen and (min-width: 62em)": {"display": "none"}}}>
  <RadixThemesBox css={{"width": "85vw"}} id={`my-form-box`} ref={ref_my_form_box}>
  <RadixFormRoot className={`Root`} css={{"width": "100%"}} onSubmit={handleSubmit_54e581d5da48387adcf7cd9a2b15226c}>
  <RadixThemesBox css={{"display": "none"}}>
  <RadixThemesTextField.Root name={`post_id`} type={`hidden`} value={state__local_auth_state__session_state__blog_post_state.post?.id}/>
</RadixThemesBox>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} direction={`column`} gap={`3`}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`row`} gap={`3`}>
  <RadixThemesTextField.Root css={{"width": "100%"}} defaultValue={state__local_auth_state__session_state__blog_post_state.post?.title} name={`title`} placeholder={`Title`} required={true} type={`text`}/>
</RadixThemesFlex>
  <DebounceInput css={{"height": "50vh", "width": "100%"}} debounceTimeout={300} element={RadixThemesTextArea} name={`content`} onChange={(_e0) => addEvents([Event("state.local_auth_state.session_state.blog_post_state.set_post_content", {value:_e0.target.value})], (_e0), {})} placeholder={`Your message`} required={true} value={state__local_auth_state__session_state__blog_post_state.post_content}/>
  <RadixThemesFlex gap={`2`}>
  <RadixThemesSwitch defaultChecked={state__local_auth_state__session_state__blog_post_state.post_publish_active} name={`publish_active`} onCheckedChange={(_checked) => addEvents([Event("state.local_auth_state.session_state.blog_post_state.set_post_publish_active", {value:_checked})], (_checked), {})}/>
  <RadixThemesText as={`p`}>
  {`Publish Active`}
</RadixThemesText>
</RadixThemesFlex>
  <Fragment>
  {isTrue(state__local_auth_state__session_state__blog_post_state.post_publish_active) ? (
  <Fragment>
  <RadixThemesBox css={{"width": "100%"}}>
  <RadixThemesFlex align={`start`} className={`rx-Stack`} css={{"width": "100%"}} direction={`row`} gap={`3`}>
  <RadixThemesTextField.Root css={{"width": "100%"}} defaultValue={state__local_auth_state__session_state__blog_post_state__blog_edit_form_state.publish_display_date} name={`publish_date`} type={`date`}/>
  <RadixThemesTextField.Root css={{"width": "100%"}} defaultValue={state__local_auth_state__session_state__blog_post_state__blog_edit_form_state.publish_display_time} name={`publish_time`} type={`time`}/>
</RadixThemesFlex>
</RadixThemesBox>
</Fragment>
) : (
  <Fragment/>
)}
</Fragment>
  <RadixThemesButton type={`submit`}>
  {`Submit`}
</RadixThemesButton>
</RadixThemesFlex>
</RadixFormRoot>
</RadixThemesBox>
</RadixThemesBox>
</RadixThemesFlex>
</Fragment>
) : (
  <Fragment>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"minHeight": "85vh"}} direction={`row`} gap={`5`}>
  <RadixThemesHeading>
  {`Blog PostNot Found`}
</RadixThemesHeading>
</RadixThemesFlex>
</Fragment>
)}
</Fragment>
</RadixThemesBox>
  <RadixThemesFlex css={{"display": "flex", "alignItems": "center", "justifyContent": "center", "width": "100%"}}>
  <RadixThemesLink asChild={true} css={{"&:hover": {"color": "var(--accent-8)"}}} size={`3`}>
  <NextLink href={`https://reflex.dev`} passHref={true}>
  <RadixThemesFlex align={`center`} className={`rx-Stack`} css={{"textAlign": "center", "padding": "1em"}} direction={`row`} gap={`3`}>
  {`Built with `}
  <Fragment>
  {isTrue(((colorMode) === (`light`))) ? (
  <Fragment>
  <div className={`rx-Html`} dangerouslySetInnerHTML={{"__html": "<svg width=\"56\" height=\"12\" viewBox=\"0 0 56 12\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\">\n<path d=\"M0 11.6V0.400024H8.96V4.88002H6.72V2.64002H2.24V4.88002H6.72V7.12002H2.24V11.6H0ZM6.72 11.6V7.12002H8.96V11.6H6.72Z\" fill=\"#110F1F\"/>\n<path d=\"M11.2 11.6V0.400024H17.92V2.64002H13.44V4.88002H17.92V7.12002H13.44V9.36002H17.92V11.6H11.2Z\" fill=\"#110F1F\"/>\n<path d=\"M20.16 11.6V0.400024H26.88V2.64002H22.4V4.88002H26.88V7.12002H22.4V11.6H20.16Z\" fill=\"#110F1F\"/>\n<path d=\"M29.12 11.6V0.400024H31.36V9.36002H35.84V11.6H29.12Z\" fill=\"#110F1F\"/>\n<path d=\"M38.08 11.6V0.400024H44.8V2.64002H40.32V4.88002H44.8V7.12002H40.32V9.36002H44.8V11.6H38.08Z\" fill=\"#110F1F\"/>\n<path d=\"M47.04 4.88002V0.400024H49.28V4.88002H47.04ZM53.76 4.88002V0.400024H56V4.88002H53.76ZM49.28 7.12002V4.88002H53.76V7.12002H49.28ZM47.04 11.6V7.12002H49.28V11.6H47.04ZM53.76 11.6V7.12002H56V11.6H53.76Z\" fill=\"#110F1F\"/>\n</svg>"}}/>
</Fragment>
) : (
  <Fragment>
  <div className={`rx-Html`} dangerouslySetInnerHTML={{"__html": "<svg width=\"56\" height=\"12\" viewBox=\"0 0 56 12\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\">\n<path d=\"M0 11.5999V0.399902H8.96V4.8799H6.72V2.6399H2.24V4.8799H6.72V7.1199H2.24V11.5999H0ZM6.72 11.5999V7.1199H8.96V11.5999H6.72Z\" fill=\"white\"/>\n<path d=\"M11.2 11.5999V0.399902H17.92V2.6399H13.44V4.8799H17.92V7.1199H13.44V9.3599H17.92V11.5999H11.2Z\" fill=\"white\"/>\n<path d=\"M20.16 11.5999V0.399902H26.88V2.6399H22.4V4.8799H26.88V7.1199H22.4V11.5999H20.16Z\" fill=\"white\"/>\n<path d=\"M29.12 11.5999V0.399902H31.36V9.3599H35.84V11.5999H29.12Z\" fill=\"white\"/>\n<path d=\"M38.08 11.5999V0.399902H44.8V2.6399H40.32V4.8799H44.8V7.1199H40.32V9.3599H44.8V11.5999H38.08Z\" fill=\"white\"/>\n<path d=\"M47.04 4.8799V0.399902H49.28V4.8799H47.04ZM53.76 4.8799V0.399902H56V4.8799H53.76ZM49.28 7.1199V4.8799H53.76V7.1199H49.28ZM47.04 11.5999V7.1199H49.28V11.5999H47.04ZM53.76 11.5999V7.1199H56V11.5999H53.76Z\" fill=\"white\"/>\n</svg>"}}/>
</Fragment>
)}
</Fragment>
</RadixThemesFlex>
</NextLink>
</RadixThemesLink>
</RadixThemesFlex>
  <RadixThemesIconButton css={{"padding": "6px", "position": "fixed", "bottom": "2rem", "left": "2rem", "background": "transparent", "color": "inherit", "zIndex": "20", "&:hover": {"cursor": "pointer"}}} onClick={toggleColorMode}>
  <Fragment>
  {isTrue(((colorMode) === (`light`))) ? (
  <Fragment>
  <LucideSunIcon css={{"color": "var(--current-color)"}}/>
</Fragment>
) : (
  <Fragment>
  <LucideMoonIcon css={{"color": "var(--current-color)"}}/>
</Fragment>
)}
</Fragment>
</RadixThemesIconButton>
</Fragment>
)}
</Fragment>
) : (
  <Fragment>
  <RadixThemesFlex css={{"display": "flex", "alignItems": "center", "justifyContent": "center"}}>
  <RadixThemesText as={`p`}>
  {`Loading...`}
</RadixThemesText>
</RadixThemesFlex>
</Fragment>
)}
</Fragment>
  )
}

export function Fragment_6499b51736be44284c15de43340cb16c () {
  const [addEvents, connectErrors] = useContext(EventLoopContext);



  return (
    <Fragment>
  {isTrue(connectErrors.length >= 2) ? (
  <Fragment>
  <RadixThemesDialog.Root css={{"zIndex": 9999}} open={connectErrors.length >= 2}>
  <RadixThemesDialog.Content>
  <RadixThemesDialog.Title>
  {`Connection Error`}
</RadixThemesDialog.Title>
  <RadixThemesText as={`p`}>
  {`Cannot connect to server: `}
  {(connectErrors.length > 0) ? connectErrors[connectErrors.length - 1].message : ''}
  {`. Check if server is reachable at `}
  {getBackendURL(env.EVENT).href}
</RadixThemesText>
</RadixThemesDialog.Content>
</RadixThemesDialog.Root>
</Fragment>
) : (
  <Fragment/>
)}
</Fragment>
  )
}

const pulse = keyframes`
    0% {
        opacity: 0;
    }
    100% {
        opacity: 1;
    }
`


export function Fragment_cb5edf864ed730e6ef1545318d0da5a2 () {
  const [addEvents, connectErrors] = useContext(EventLoopContext);



  return (
    <Fragment>
  {isTrue(connectErrors.length > 0) ? (
  <Fragment>
  <LucideWifiOffIcon css={{"color": "crimson", "zIndex": 9999, "position": "fixed", "bottom": "30px", "right": "30px", "animation": `${pulse} 1s infinite`}} size={32}/>
</Fragment>
) : (
  <Fragment/>
)}
</Fragment>
  )
}

export default function Component() {

  return (
    <Fragment>
  <Fragment>
  <div css={{"position": "fixed", "width": "100vw", "height": "0"}}>
  <Fragment_cb5edf864ed730e6ef1545318d0da5a2/>
</div>
  <Fragment_6499b51736be44284c15de43340cb16c/>
</Fragment>
  <Fragment>
  <Fragment_b3f78fefb515fde8e224782a994a7310/>
</Fragment>
  <NextHead>
  <title>
  {`Full Stack Python | Blog/[Blog Id]/Edit`}
</title>
  <meta content={`favicon.ico`} property={`og:image`}/>
</NextHead>
</Fragment>
  )
}
