def register_admin_routes(bp, controller):
    bp.route("/admin_dashboard")(controller.admin_dashboard)
    bp.route("/approve_events")(controller.approve_events)
    bp.route("/approve_event/<int:event_id>", methods=["POST"])(controller.approve_event_action)
    bp.route("/manage_users")(controller.manage_users)
    bp.route("/delete_user/<int:user_id>", methods=["POST"])(controller.delete_user)
    bp.route("/change_user_role/<int:user_id>", methods=["POST"])(controller.change_user_role)
    bp.route("/manage_categories", methods=["GET", "POST"])(controller.manage_categories)
    bp.route("/delete_category/<int:category_id>", methods=["POST"])(controller.delete_category)
