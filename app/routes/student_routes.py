def register_student_routes(bp, controller):
    bp.route("/student_dashboard")(controller.student_dashboard)
    bp.route("/register_for_event", methods=["POST"])(controller.register_for_event)
    bp.route("/cancel_registration/<int:registration_id>", methods=["POST"])(controller.cancel_registration)
    bp.route("/download_certificate/<int:registration_id>")(controller.download_certificate)
