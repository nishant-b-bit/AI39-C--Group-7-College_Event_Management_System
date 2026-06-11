def register_public_routes(bp, controller):
    bp.route("/")(controller.home)
    bp.route("/about")(controller.about)
    bp.route("/contact")(controller.contact)


def register_auth_routes(bp, controller):
    bp.route("/login", methods=["GET", "POST"])(controller.login)
    bp.route("/signup", methods=["GET", "POST"])(controller.register)
    bp.route("/logout")(controller.logout)
    bp.route("/edit_profile", methods=["GET", "POST"])(controller.edit_profile)
    bp.route("/change_password", methods=["GET", "POST"])(controller.change_password)
    bp.route("/reset_password", methods=["GET", "POST"])(controller.reset_password)
    bp.route("/notifications")(controller.notifications)
    bp.route("/notifications/<int:notification_id>/delete", methods=["POST"])(controller.delete_notification)
    bp.route("/notifications/clear", methods=["POST"])(controller.clear_notifications)


def register_event_routes(bp, controller):
    bp.route("/view_events")(controller.view_events)
    bp.route("/event_details")(controller.eventdetails)
