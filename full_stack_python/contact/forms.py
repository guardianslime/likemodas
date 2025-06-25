import reflex as rx 


from .state import (
    ContactAddEntrytFormState,
    ContactEditFormState
)


def contact_post_add_form() -> rx.Component:
    return rx.form(
            rx.vstack(
                rx.hstack(
                    rx.input(
                        name="title",
                        placeholder="Title",
                        required=False,
                        type= "text",
                        width="100%",
                    ),

                    width="100%",
                ),
                rx.text_area(
                    name="content",
                    placeholder="Your message",
                    required=True,
                    height='50vh',
                    width='100%',
                ),
                rx.button("Submit", type="submit"),
            ),
            on_submit=ContactAddEntrytFormState.handle_submit,
            reset_on_submit=True,
    )


from .state import ContactEditFormState

def contact_post_edit_form() -> rx.Component:
    entry = ContactEditFormState.entry
    title = entry.title
    publish_active = entry.publish_active
    entry_content = ContactEditFormState.entry_content
    return rx.form(
            rx.box(
                rx.input(
                    type='hidden',
                    name='entry_id',
                    value=entry.id
                ),
                display='none'
            ),
            rx.vstack(
                rx.hstack(
                    rx.input(
                        default_value=title,
                        name="title",
                        placeholder="Title",
                        required=True,
                        type='text',
                        width='100%',
                    ),
                    width='100%',
                ),
                rx.text_area(
                    value = entry_content,
                    on_change = ContactEditFormState.set_entry_content,
                    name='content',
                    placeholder='Your message',
                    required=True,
                    height='50vh',
                    width='100%',
                ),
                rx.flex(
                    rx.switch(
                        default_checked=ContactEditFormState.
                        entry_publish_active,
                        on_change=ContactEditFormState.set_entry_publish_active,
                        name='publish_active',        
                    ),
                    rx.text("Publish Active"),
                    spacing="2",
                ),
                rx.cond(
                    ContactEditFormState.entry_publish_active,
                    rx.box(
                        rx.hstack(
                            rx.input(
                                default_value=ContactEditFormState.
                                publish_display_date,
                                type='date',
                                name='publish_date',
                                width='100%'
                            ),
                            rx.input(
                                default_value=ContactEditFormState.
                                publish_display_time,
                                type='time',
                                name='publish_time',
                                width='100%'
                            ),
                        width='100%'
                        ),
                        width='100%'
                    )
                ),
                rx.button("Submit", type="submit"),
            ),
            on_submit=ContactEditFormState.handle_submit,
    )
