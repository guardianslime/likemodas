import { createContext, useContext, useMemo, useReducer, useState } from "react"
import { applyDelta, Event, hydrateClientStorage, useEventLoop, refs } from "/utils/state.js"

export const initialState = {"state": {"is_hydrated": false, "router": {"session": {"client_token": "", "client_ip": "", "session_id": ""}, "headers": {"host": "", "origin": "", "upgrade": "", "connection": "", "pragma": "", "cache_control": "", "user_agent": "", "sec_websocket_version": "", "sec_websocket_key": "", "sec_websocket_extensions": "", "accept_encoding": "", "accept_language": ""}, "page": {"host": "", "path": "", "raw_path": "", "full_path": "", "full_raw_path": "", "params": {}}}}, "state.nav_state": {}, "state.update_vars_internal_state": {}, "state.local_auth_state": {"auth_token": ""}, "state.local_auth_state.login_state": {"error_message": "", "redirect_to": ""}, "state.local_auth_state.registration_state": {"error_message": "", "new_user_id": -1, "success": false}, "state.local_auth_state.registration_state.my_register_state": {}, "state.local_auth_state.session_state": {}, "state.local_auth_state.session_state.contact_state": {"did_submit": false, "entries": [], "form_data": {}}, "state.local_auth_state.session_state.article_public_state": {"limit": 20, "post": null, "post_content": "", "post_publish_active": false, "posts": []}, "state.local_auth_state.session_state.blog_post_state": {"post": null, "post_content": "", "post_publish_active": false, "posts": []}, "state.local_auth_state.session_state.blog_post_state.blog_add_post_form_state": {"form_data": {}}, "state.local_auth_state.session_state.blog_post_state.blog_edit_form_state": {"form_data": {}}, "state.on_load_internal_state": {}}

export const defaultColorMode = "dark"
export const ColorModeContext = createContext(null);
export const UploadFilesContext = createContext(null);
export const DispatchContext = createContext(null);
export const StateContexts = {
  state: createContext(null),
  state__nav_state: createContext(null),
  state__update_vars_internal_state: createContext(null),
  state__local_auth_state: createContext(null),
  state__local_auth_state__login_state: createContext(null),
  state__local_auth_state__registration_state: createContext(null),
  state__local_auth_state__registration_state__my_register_state: createContext(null),
  state__local_auth_state__session_state: createContext(null),
  state__local_auth_state__session_state__contact_state: createContext(null),
  state__local_auth_state__session_state__article_public_state: createContext(null),
  state__local_auth_state__session_state__blog_post_state: createContext(null),
  state__local_auth_state__session_state__blog_post_state__blog_add_post_form_state: createContext(null),
  state__local_auth_state__session_state__blog_post_state__blog_edit_form_state: createContext(null),
  state__on_load_internal_state: createContext(null),
}
export const EventLoopContext = createContext(null);
export const clientStorage = {"cookies": {}, "local_storage": {"state.local_auth_state.auth_token": {"name": "_auth_token", "sync": false}}}

export const state_name = "state"

// Theses events are triggered on initial load and each page navigation.
export const onLoadInternalEvent = () => {
    const internal_events = [];

    // Get tracked cookie and local storage vars to send to the backend.
    const client_storage_vars = hydrateClientStorage(clientStorage);
    // But only send the vars if any are actually set in the browser.
    if (client_storage_vars && Object.keys(client_storage_vars).length !== 0) {
        internal_events.push(
            Event(
                'state.update_vars_internal_state.update_vars_internal',
                {vars: client_storage_vars},
            ),
        );
    }

    // `on_load_internal` triggers the correct on_load event(s) for the current page.
    // If the page does not define any on_load event, this will just set `is_hydrated = true`.
    internal_events.push(Event('state.on_load_internal_state.on_load_internal'));

    return internal_events;
}

// The following events are sent when the websocket connects or reconnects.
export const initialEvents = () => [
    Event('state.hydrate'),
    ...onLoadInternalEvent()
]

export const isDevMode = true

export function UploadFilesProvider({ children }) {
  const [filesById, setFilesById] = useState({})
  refs["__clear_selected_files"] = (id) => setFilesById(filesById => {
    const newFilesById = {...filesById}
    delete newFilesById[id]
    return newFilesById
  })
  return (
    <UploadFilesContext.Provider value={[filesById, setFilesById]}>
      {children}
    </UploadFilesContext.Provider>
  )
}

export function EventLoopProvider({ children }) {
  const dispatch = useContext(DispatchContext)
  const [addEvents, connectErrors] = useEventLoop(
    dispatch,
    initialEvents,
    clientStorage,
  )
  return (
    <EventLoopContext.Provider value={[addEvents, connectErrors]}>
      {children}
    </EventLoopContext.Provider>
  )
}

export function StateProvider({ children }) {
  const [state, dispatch_state] = useReducer(applyDelta, initialState["state"])
  const [state__nav_state, dispatch_state__nav_state] = useReducer(applyDelta, initialState["state.nav_state"])
  const [state__update_vars_internal_state, dispatch_state__update_vars_internal_state] = useReducer(applyDelta, initialState["state.update_vars_internal_state"])
  const [state__local_auth_state, dispatch_state__local_auth_state] = useReducer(applyDelta, initialState["state.local_auth_state"])
  const [state__local_auth_state__login_state, dispatch_state__local_auth_state__login_state] = useReducer(applyDelta, initialState["state.local_auth_state.login_state"])
  const [state__local_auth_state__registration_state, dispatch_state__local_auth_state__registration_state] = useReducer(applyDelta, initialState["state.local_auth_state.registration_state"])
  const [state__local_auth_state__registration_state__my_register_state, dispatch_state__local_auth_state__registration_state__my_register_state] = useReducer(applyDelta, initialState["state.local_auth_state.registration_state.my_register_state"])
  const [state__local_auth_state__session_state, dispatch_state__local_auth_state__session_state] = useReducer(applyDelta, initialState["state.local_auth_state.session_state"])
  const [state__local_auth_state__session_state__contact_state, dispatch_state__local_auth_state__session_state__contact_state] = useReducer(applyDelta, initialState["state.local_auth_state.session_state.contact_state"])
  const [state__local_auth_state__session_state__article_public_state, dispatch_state__local_auth_state__session_state__article_public_state] = useReducer(applyDelta, initialState["state.local_auth_state.session_state.article_public_state"])
  const [state__local_auth_state__session_state__blog_post_state, dispatch_state__local_auth_state__session_state__blog_post_state] = useReducer(applyDelta, initialState["state.local_auth_state.session_state.blog_post_state"])
  const [state__local_auth_state__session_state__blog_post_state__blog_add_post_form_state, dispatch_state__local_auth_state__session_state__blog_post_state__blog_add_post_form_state] = useReducer(applyDelta, initialState["state.local_auth_state.session_state.blog_post_state.blog_add_post_form_state"])
  const [state__local_auth_state__session_state__blog_post_state__blog_edit_form_state, dispatch_state__local_auth_state__session_state__blog_post_state__blog_edit_form_state] = useReducer(applyDelta, initialState["state.local_auth_state.session_state.blog_post_state.blog_edit_form_state"])
  const [state__on_load_internal_state, dispatch_state__on_load_internal_state] = useReducer(applyDelta, initialState["state.on_load_internal_state"])
  const dispatchers = useMemo(() => {
    return {
      "state": dispatch_state,
      "state.nav_state": dispatch_state__nav_state,
      "state.update_vars_internal_state": dispatch_state__update_vars_internal_state,
      "state.local_auth_state": dispatch_state__local_auth_state,
      "state.local_auth_state.login_state": dispatch_state__local_auth_state__login_state,
      "state.local_auth_state.registration_state": dispatch_state__local_auth_state__registration_state,
      "state.local_auth_state.registration_state.my_register_state": dispatch_state__local_auth_state__registration_state__my_register_state,
      "state.local_auth_state.session_state": dispatch_state__local_auth_state__session_state,
      "state.local_auth_state.session_state.contact_state": dispatch_state__local_auth_state__session_state__contact_state,
      "state.local_auth_state.session_state.article_public_state": dispatch_state__local_auth_state__session_state__article_public_state,
      "state.local_auth_state.session_state.blog_post_state": dispatch_state__local_auth_state__session_state__blog_post_state,
      "state.local_auth_state.session_state.blog_post_state.blog_add_post_form_state": dispatch_state__local_auth_state__session_state__blog_post_state__blog_add_post_form_state,
      "state.local_auth_state.session_state.blog_post_state.blog_edit_form_state": dispatch_state__local_auth_state__session_state__blog_post_state__blog_edit_form_state,
      "state.on_load_internal_state": dispatch_state__on_load_internal_state,
    }
  }, [])

  return (
    <StateContexts.state.Provider value={ state }>
    <StateContexts.state__nav_state.Provider value={ state__nav_state }>
    <StateContexts.state__update_vars_internal_state.Provider value={ state__update_vars_internal_state }>
    <StateContexts.state__local_auth_state.Provider value={ state__local_auth_state }>
    <StateContexts.state__local_auth_state__login_state.Provider value={ state__local_auth_state__login_state }>
    <StateContexts.state__local_auth_state__registration_state.Provider value={ state__local_auth_state__registration_state }>
    <StateContexts.state__local_auth_state__registration_state__my_register_state.Provider value={ state__local_auth_state__registration_state__my_register_state }>
    <StateContexts.state__local_auth_state__session_state.Provider value={ state__local_auth_state__session_state }>
    <StateContexts.state__local_auth_state__session_state__contact_state.Provider value={ state__local_auth_state__session_state__contact_state }>
    <StateContexts.state__local_auth_state__session_state__article_public_state.Provider value={ state__local_auth_state__session_state__article_public_state }>
    <StateContexts.state__local_auth_state__session_state__blog_post_state.Provider value={ state__local_auth_state__session_state__blog_post_state }>
    <StateContexts.state__local_auth_state__session_state__blog_post_state__blog_add_post_form_state.Provider value={ state__local_auth_state__session_state__blog_post_state__blog_add_post_form_state }>
    <StateContexts.state__local_auth_state__session_state__blog_post_state__blog_edit_form_state.Provider value={ state__local_auth_state__session_state__blog_post_state__blog_edit_form_state }>
    <StateContexts.state__on_load_internal_state.Provider value={ state__on_load_internal_state }>
      <DispatchContext.Provider value={dispatchers}>
        {children}
      </DispatchContext.Provider>
    </StateContexts.state__on_load_internal_state.Provider>
    </StateContexts.state__local_auth_state__session_state__blog_post_state__blog_edit_form_state.Provider>
    </StateContexts.state__local_auth_state__session_state__blog_post_state__blog_add_post_form_state.Provider>
    </StateContexts.state__local_auth_state__session_state__blog_post_state.Provider>
    </StateContexts.state__local_auth_state__session_state__article_public_state.Provider>
    </StateContexts.state__local_auth_state__session_state__contact_state.Provider>
    </StateContexts.state__local_auth_state__session_state.Provider>
    </StateContexts.state__local_auth_state__registration_state__my_register_state.Provider>
    </StateContexts.state__local_auth_state__registration_state.Provider>
    </StateContexts.state__local_auth_state__login_state.Provider>
    </StateContexts.state__local_auth_state.Provider>
    </StateContexts.state__update_vars_internal_state.Provider>
    </StateContexts.state__nav_state.Provider>
    </StateContexts.state.Provider>
  )
}