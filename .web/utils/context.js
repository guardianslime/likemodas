import { createContext, useContext, useMemo, useReducer, useState } from "react"
import { applyDelta, Event, hydrateClientStorage, useEventLoop, refs } from "$/utils/state.js"

export const initialState = {"reflex___state____state": {"blog_id": "", "is_hydrated": false, "router": {"session": {"client_token": "", "client_ip": "", "session_id": ""}, "headers": {"host": "", "origin": "", "upgrade": "", "connection": "", "cookie": "", "pragma": "", "cache_control": "", "user_agent": "", "sec_websocket_version": "", "sec_websocket_key": "", "sec_websocket_extensions": "", "accept_encoding": "", "accept_language": ""}, "page": {"host": "", "path": "", "raw_path": "", "full_path": "", "full_raw_path": "", "params": {}}}}, "reflex___state____state.full_stack_python___contact___state____contact_state": {"did_submit": false, "entries": [], "form_data": {}, "thank_you": "Thank you !!"}, "reflex___state____state.reflex___state____update_vars_internal_state": {}, "reflex___state____state.full_stack_python___blog___state____blog_post_state": {"blog_post_edit_url": "/blog", "blog_post_id": "", "blog_post_url": "/blog", "post": null, "post_content": "", "post_publish_active": false, "posts": []}, "reflex___state____state.full_stack_python___blog___state____blog_post_state.full_stack_python___blog___state____blog_add_post_form_state": {"form_data": {}}, "reflex___state____state.full_stack_python___blog___state____blog_post_state.full_stack_python___blog___state____blog_edit_form_state": {"form_data": {}, "publish_display_date": "2025-06-06", "publish_display_time": "15:34:16"}, "reflex___state____state.reflex___state____frontend_event_exception_state": {}, "reflex___state____state.full_stack_python___navigation___state____nav_state": {}, "reflex___state____state.reflex_local_auth___local_auth____local_auth_state": {"auth_token": "", "authenticated_user": {"id": -1, "username": null, "enabled": false}, "is_authenticated": false}, "reflex___state____state.reflex_local_auth___local_auth____local_auth_state.reflex_local_auth___registration____registration_state": {"error_message": "", "new_user_id": -1, "success": false}, "reflex___state____state.reflex_local_auth___local_auth____local_auth_state.reflex_local_auth___registration____registration_state.full_stack_python___auth___state____my_register_state": {}, "reflex___state____state.reflex_local_auth___local_auth____local_auth_state.reflex_local_auth___login____login_state": {"error_message": "", "redirect_to": ""}, "reflex___state____state.reflex_local_auth___local_auth____local_auth_state.full_stack_python___auth___state____session_state": {"authenticated_user_info": null, "authenticated_username": null}, "reflex___state____state.full_stack_python___full_stack_python____state": {"label": "Welcome to Reflex"}, "reflex___state____state.reflex___state____on_load_internal_state": {}}

export const defaultColorMode = "system"
export const ColorModeContext = createContext(null);
export const UploadFilesContext = createContext(null);
export const DispatchContext = createContext(null);
export const StateContexts = {
  reflex___state____state: createContext(null),
  reflex___state____state__full_stack_python___contact___state____contact_state: createContext(null),
  reflex___state____state__reflex___state____update_vars_internal_state: createContext(null),
  reflex___state____state__full_stack_python___blog___state____blog_post_state: createContext(null),
  reflex___state____state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_add_post_form_state: createContext(null),
  reflex___state____state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_edit_form_state: createContext(null),
  reflex___state____state__reflex___state____frontend_event_exception_state: createContext(null),
  reflex___state____state__full_stack_python___navigation___state____nav_state: createContext(null),
  reflex___state____state__reflex_local_auth___local_auth____local_auth_state: createContext(null),
  reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___registration____registration_state: createContext(null),
  reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___registration____registration_state__full_stack_python___auth___state____my_register_state: createContext(null),
  reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___login____login_state: createContext(null),
  reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state: createContext(null),
  reflex___state____state__full_stack_python___full_stack_python____state: createContext(null),
  reflex___state____state__reflex___state____on_load_internal_state: createContext(null),
}
export const EventLoopContext = createContext(null);
export const clientStorage = {"cookies": {}, "local_storage": {"reflex___state____state.reflex_local_auth___local_auth____local_auth_state.auth_token": {"name": "_auth_token", "sync": false}}, "session_storage": {}}

export const state_name = "reflex___state____state"

export const exception_state_name = "reflex___state____state.reflex___state____frontend_event_exception_state"

// These events are triggered on initial load and each page navigation.
export const onLoadInternalEvent = () => {
    const internal_events = [];

    // Get tracked cookie and local storage vars to send to the backend.
    const client_storage_vars = hydrateClientStorage(clientStorage);
    // But only send the vars if any are actually set in the browser.
    if (client_storage_vars && Object.keys(client_storage_vars).length !== 0) {
        internal_events.push(
            Event(
                'reflex___state____state.reflex___state____update_vars_internal_state.update_vars_internal',
                {vars: client_storage_vars},
            ),
        );
    }

    // `on_load_internal` triggers the correct on_load event(s) for the current page.
    // If the page does not define any on_load event, this will just set `is_hydrated = true`.
    internal_events.push(Event('reflex___state____state.reflex___state____on_load_internal_state.on_load_internal'));

    return internal_events;
}

// The following events are sent when the websocket connects or reconnects.
export const initialEvents = () => [
    Event('reflex___state____state.hydrate'),
    ...onLoadInternalEvent()
]

export const isDevMode = true

export const lastCompiledTimeStamp = "2025-06-06 15:34:16.344985"

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
  const [reflex___state____state, dispatch_reflex___state____state] = useReducer(applyDelta, initialState["reflex___state____state"])
  const [reflex___state____state__full_stack_python___contact___state____contact_state, dispatch_reflex___state____state__full_stack_python___contact___state____contact_state] = useReducer(applyDelta, initialState["reflex___state____state.full_stack_python___contact___state____contact_state"])
  const [reflex___state____state__reflex___state____update_vars_internal_state, dispatch_reflex___state____state__reflex___state____update_vars_internal_state] = useReducer(applyDelta, initialState["reflex___state____state.reflex___state____update_vars_internal_state"])
  const [reflex___state____state__full_stack_python___blog___state____blog_post_state, dispatch_reflex___state____state__full_stack_python___blog___state____blog_post_state] = useReducer(applyDelta, initialState["reflex___state____state.full_stack_python___blog___state____blog_post_state"])
  const [reflex___state____state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_add_post_form_state, dispatch_reflex___state____state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_add_post_form_state] = useReducer(applyDelta, initialState["reflex___state____state.full_stack_python___blog___state____blog_post_state.full_stack_python___blog___state____blog_add_post_form_state"])
  const [reflex___state____state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_edit_form_state, dispatch_reflex___state____state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_edit_form_state] = useReducer(applyDelta, initialState["reflex___state____state.full_stack_python___blog___state____blog_post_state.full_stack_python___blog___state____blog_edit_form_state"])
  const [reflex___state____state__reflex___state____frontend_event_exception_state, dispatch_reflex___state____state__reflex___state____frontend_event_exception_state] = useReducer(applyDelta, initialState["reflex___state____state.reflex___state____frontend_event_exception_state"])
  const [reflex___state____state__full_stack_python___navigation___state____nav_state, dispatch_reflex___state____state__full_stack_python___navigation___state____nav_state] = useReducer(applyDelta, initialState["reflex___state____state.full_stack_python___navigation___state____nav_state"])
  const [reflex___state____state__reflex_local_auth___local_auth____local_auth_state, dispatch_reflex___state____state__reflex_local_auth___local_auth____local_auth_state] = useReducer(applyDelta, initialState["reflex___state____state.reflex_local_auth___local_auth____local_auth_state"])
  const [reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___registration____registration_state, dispatch_reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___registration____registration_state] = useReducer(applyDelta, initialState["reflex___state____state.reflex_local_auth___local_auth____local_auth_state.reflex_local_auth___registration____registration_state"])
  const [reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___registration____registration_state__full_stack_python___auth___state____my_register_state, dispatch_reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___registration____registration_state__full_stack_python___auth___state____my_register_state] = useReducer(applyDelta, initialState["reflex___state____state.reflex_local_auth___local_auth____local_auth_state.reflex_local_auth___registration____registration_state.full_stack_python___auth___state____my_register_state"])
  const [reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___login____login_state, dispatch_reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___login____login_state] = useReducer(applyDelta, initialState["reflex___state____state.reflex_local_auth___local_auth____local_auth_state.reflex_local_auth___login____login_state"])
  const [reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state, dispatch_reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state] = useReducer(applyDelta, initialState["reflex___state____state.reflex_local_auth___local_auth____local_auth_state.full_stack_python___auth___state____session_state"])
  const [reflex___state____state__full_stack_python___full_stack_python____state, dispatch_reflex___state____state__full_stack_python___full_stack_python____state] = useReducer(applyDelta, initialState["reflex___state____state.full_stack_python___full_stack_python____state"])
  const [reflex___state____state__reflex___state____on_load_internal_state, dispatch_reflex___state____state__reflex___state____on_load_internal_state] = useReducer(applyDelta, initialState["reflex___state____state.reflex___state____on_load_internal_state"])
  const dispatchers = useMemo(() => {
    return {
      "reflex___state____state": dispatch_reflex___state____state,
      "reflex___state____state.full_stack_python___contact___state____contact_state": dispatch_reflex___state____state__full_stack_python___contact___state____contact_state,
      "reflex___state____state.reflex___state____update_vars_internal_state": dispatch_reflex___state____state__reflex___state____update_vars_internal_state,
      "reflex___state____state.full_stack_python___blog___state____blog_post_state": dispatch_reflex___state____state__full_stack_python___blog___state____blog_post_state,
      "reflex___state____state.full_stack_python___blog___state____blog_post_state.full_stack_python___blog___state____blog_add_post_form_state": dispatch_reflex___state____state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_add_post_form_state,
      "reflex___state____state.full_stack_python___blog___state____blog_post_state.full_stack_python___blog___state____blog_edit_form_state": dispatch_reflex___state____state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_edit_form_state,
      "reflex___state____state.reflex___state____frontend_event_exception_state": dispatch_reflex___state____state__reflex___state____frontend_event_exception_state,
      "reflex___state____state.full_stack_python___navigation___state____nav_state": dispatch_reflex___state____state__full_stack_python___navigation___state____nav_state,
      "reflex___state____state.reflex_local_auth___local_auth____local_auth_state": dispatch_reflex___state____state__reflex_local_auth___local_auth____local_auth_state,
      "reflex___state____state.reflex_local_auth___local_auth____local_auth_state.reflex_local_auth___registration____registration_state": dispatch_reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___registration____registration_state,
      "reflex___state____state.reflex_local_auth___local_auth____local_auth_state.reflex_local_auth___registration____registration_state.full_stack_python___auth___state____my_register_state": dispatch_reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___registration____registration_state__full_stack_python___auth___state____my_register_state,
      "reflex___state____state.reflex_local_auth___local_auth____local_auth_state.reflex_local_auth___login____login_state": dispatch_reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___login____login_state,
      "reflex___state____state.reflex_local_auth___local_auth____local_auth_state.full_stack_python___auth___state____session_state": dispatch_reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state,
      "reflex___state____state.full_stack_python___full_stack_python____state": dispatch_reflex___state____state__full_stack_python___full_stack_python____state,
      "reflex___state____state.reflex___state____on_load_internal_state": dispatch_reflex___state____state__reflex___state____on_load_internal_state,
    }
  }, [])

  return (
    <StateContexts.reflex___state____state.Provider value={ reflex___state____state }>
    <StateContexts.reflex___state____state__full_stack_python___contact___state____contact_state.Provider value={ reflex___state____state__full_stack_python___contact___state____contact_state }>
    <StateContexts.reflex___state____state__reflex___state____update_vars_internal_state.Provider value={ reflex___state____state__reflex___state____update_vars_internal_state }>
    <StateContexts.reflex___state____state__full_stack_python___blog___state____blog_post_state.Provider value={ reflex___state____state__full_stack_python___blog___state____blog_post_state }>
    <StateContexts.reflex___state____state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_add_post_form_state.Provider value={ reflex___state____state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_add_post_form_state }>
    <StateContexts.reflex___state____state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_edit_form_state.Provider value={ reflex___state____state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_edit_form_state }>
    <StateContexts.reflex___state____state__reflex___state____frontend_event_exception_state.Provider value={ reflex___state____state__reflex___state____frontend_event_exception_state }>
    <StateContexts.reflex___state____state__full_stack_python___navigation___state____nav_state.Provider value={ reflex___state____state__full_stack_python___navigation___state____nav_state }>
    <StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state.Provider value={ reflex___state____state__reflex_local_auth___local_auth____local_auth_state }>
    <StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___registration____registration_state.Provider value={ reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___registration____registration_state }>
    <StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___registration____registration_state__full_stack_python___auth___state____my_register_state.Provider value={ reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___registration____registration_state__full_stack_python___auth___state____my_register_state }>
    <StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___login____login_state.Provider value={ reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___login____login_state }>
    <StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state.Provider value={ reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state }>
    <StateContexts.reflex___state____state__full_stack_python___full_stack_python____state.Provider value={ reflex___state____state__full_stack_python___full_stack_python____state }>
    <StateContexts.reflex___state____state__reflex___state____on_load_internal_state.Provider value={ reflex___state____state__reflex___state____on_load_internal_state }>
      <DispatchContext.Provider value={dispatchers}>
        {children}
      </DispatchContext.Provider>
    </StateContexts.reflex___state____state__reflex___state____on_load_internal_state.Provider>
    </StateContexts.reflex___state____state__full_stack_python___full_stack_python____state.Provider>
    </StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__full_stack_python___auth___state____session_state.Provider>
    </StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___login____login_state.Provider>
    </StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___registration____registration_state__full_stack_python___auth___state____my_register_state.Provider>
    </StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state__reflex_local_auth___registration____registration_state.Provider>
    </StateContexts.reflex___state____state__reflex_local_auth___local_auth____local_auth_state.Provider>
    </StateContexts.reflex___state____state__full_stack_python___navigation___state____nav_state.Provider>
    </StateContexts.reflex___state____state__reflex___state____frontend_event_exception_state.Provider>
    </StateContexts.reflex___state____state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_edit_form_state.Provider>
    </StateContexts.reflex___state____state__full_stack_python___blog___state____blog_post_state__full_stack_python___blog___state____blog_add_post_form_state.Provider>
    </StateContexts.reflex___state____state__full_stack_python___blog___state____blog_post_state.Provider>
    </StateContexts.reflex___state____state__reflex___state____update_vars_internal_state.Provider>
    </StateContexts.reflex___state____state__full_stack_python___contact___state____contact_state.Provider>
    </StateContexts.reflex___state____state.Provider>
  )
}