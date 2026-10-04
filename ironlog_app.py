"""
IRONLOG — Gym Management Dashboard (Streamlit)
 
Run with:
    pip install streamlit
    streamlit run ironlog_app.py
"""
 
import streamlit as st
from abc import ABC, abstractmethod
from datetime import date
 
# =====================================================================
# OOP MODEL
# =====================================================================
 
class Membership(ABC):
    """Abstract base class — ABSTRACTION."""
 
    def __init__(self, base_fee: float, duration_months: int):
        self._base_fee = base_fee              # ENCAPSULATION
        self._duration_months = duration_months
 
    @property
    def base_fee(self):
        return self._base_fee
 
    @base_fee.setter
    def base_fee(self, value):
        if value < 0:
            raise ValueError("Base fee cannot be negative")
        self._base_fee = value
 
    @property
    def duration_months(self):
        return self._duration_months
 
    @duration_months.setter
    def duration_months(self, value):
        if value < 1:
            raise ValueError("Duration must be at least 1 month")
        self._duration_months = value
 
    @abstractmethod
    def calculate_fee(self) -> float: ...
 
    @abstractmethod
    def plan_name(self) -> str: ...
 
    @abstractmethod
    def formula(self) -> str: ...
 
 
class BasicMembership(Membership):          # INHERITANCE
    def calculate_fee(self):                 # OVERRIDING
        return self._base_fee * self._duration_months
 
    def plan_name(self):
        return "Basic"
 
    def formula(self):
        return "base_fee × duration"
 
 
class StandardMembership(Membership):
    def __init__(self, base_fee, duration_months, class_fee=200):
        super().__init__(base_fee, duration_months)
        self._class_fee = class_fee
 
    def calculate_fee(self):
        return (self._base_fee + self._class_fee) * self._duration_months
 
    def plan_name(self):
        return "Standard"
 
    def formula(self):
        return "(base_fee + class_fee) × duration"
 
 
class PremiumMembership(Membership):
    def __init__(self, base_fee, duration_months, class_fee=300, nutrition_fee=200):
        super().__init__(base_fee, duration_months)
        self._class_fee = class_fee
        self._nutrition_fee = nutrition_fee
 
    def calculate_fee(self):
        return (self._base_fee + self._class_fee + self._nutrition_fee) * self._duration_months
 
    def plan_name(self):
        return "Premium"
 
    def formula(self):
        return "(base_fee + class_fee + nutrition_fee) × duration"
 
 
class PlatinumMembership(Membership):
    def __init__(self, base_fee, duration_months, trainer_fee=500, sessions_per_month=4):
        super().__init__(base_fee, duration_months)
        self._trainer_fee = trainer_fee
        self._sessions_per_month = sessions_per_month
 
    def calculate_fee(self):
        return (self._base_fee * self._duration_months) + \
               (self._trainer_fee * self._sessions_per_month * self._duration_months)
 
    def plan_name(self):
        return "Platinum"
 
    def formula(self):
        return "(base_fee × duration) + (trainer_fee × sessions × duration)"
 
 
PLAN_CLASSES = {
    "Basic": BasicMembership,
    "Standard": StandardMembership,
    "Premium": PremiumMembership,
    "Platinum": PlatinumMembership,
}
 
PLAN_FIELD_LABELS = {
    "base_fee": "Base Fee (₹ / month)",
    "class_fee": "Group Class Fee (₹ / month)",
    "nutrition_fee": "Nutrition Plan Fee (₹ / month)",
    "trainer_fee": "Trainer Fee (₹ / session)",
    "sessions": "Sessions / month",
    "renewal_discount": "Renewal Discount (%)",
}
 
 
class Trainer:
    def __init__(self, trainer_id, name, specialization, experience_years):
        self.trainer_id = trainer_id
        self.name = name
        self.specialization = specialization
        self.experience_years = experience_years
 
 
class GymMember:
    """Holds a Membership object (composition) and a list of Trainers —
    fee is computed POLYMORPHICALLY through whichever subclass was assigned."""
 
    def __init__(self, member_id, name, membership: Membership, trainers=None):
        self.member_id = member_id
        self.name = name
        self.membership = membership
        self.trainers = trainers if trainers is not None else []
        self.active = True
        self.join_date = date.today()
 
    def calculate_fee(self):
        return self.membership.calculate_fee()   # POLYMORPHISM
 
    def renew(self, extra_months: int, discount_percent: float = 0):
        """Python has no true function overloading — a default parameter
        approximates the two renewMembership() overloads from the C++ version."""
        self.active = True
        self.membership.duration_months += extra_months
        if discount_percent:
            self.membership.base_fee = round(self.membership.base_fee * (1 - discount_percent / 100))
 
 
class Payment:
    def __init__(self, payment_id, member_id, amount, method, status="Paid"):
        self.payment_id = payment_id
        self.member_id = member_id
        self.amount = amount
        self.method = method
        self.status = status
        self.date = date.today()
 
 
def get_trainer_by_name(name):
    return next((t for t in st.session_state.trainers if t.name == name), None)
 
 
# =====================================================================
# APP STATE
# =====================================================================
 
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "ironlog123"
 
 
def init_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
 
    if "plan_config" not in st.session_state:
        st.session_state.plan_config = {
            "Basic": {"base_fee": 1000, "renewal_discount": 5},
            "Standard": {"base_fee": 1200, "class_fee": 300, "renewal_discount": 10},
            "Premium": {"base_fee": 1000, "class_fee": 300, "nutrition_fee": 200, "renewal_discount": 10},
            "Platinum": {"base_fee": 1500, "trainer_fee": 500, "sessions": 4, "renewal_discount": 15},
        }
 
    if "trainers" not in st.session_state:
        st.session_state.trainers = [
            Trainer("T001", "Rohit", "Boxing", 6),
            Trainer("T002", "Sanket", "Stretching & Aerobics", 4),
            Trainer("T003", "Karan Mehta", "Strength", 5),
            Trainer("T004", "Divya Rao", "Yoga", 3),
        ]
        st.session_state.trainer_counter = 4
 
    if "members" not in st.session_state:
        rohit, sanket, karan, divya = st.session_state.trainers
 
        m1 = GymMember("M001", "Rahul Sharma", BasicMembership(1000, 3), [])
        m2 = GymMember("M002", "Sneha Patil", StandardMembership(1200, 6, 300), [karan])
        m3 = GymMember("M003", "Priya Nair", PremiumMembership(1000, 9, 300, 200), [rohit, divya])
        m4 = GymMember("M004", "Amit Verma", PlatinumMembership(1500, 12, 500, 4), [rohit, sanket])
        st.session_state.members = [m1, m2, m3, m4]
        st.session_state.member_counter = 4
 
    if "payments" not in st.session_state:
        p1 = Payment("P001", "M002", st.session_state.members[1].calculate_fee(), "UPI")
        p2 = Payment("P002", "M004", st.session_state.members[3].calculate_fee(), "Card")
        st.session_state.payments = [p1, p2]
        st.session_state.payment_counter = 2
 
    if "dashboard_view" not in st.session_state:
        st.session_state.dashboard_view = None
 
 
# =====================================================================
# LOGIN PAGE
# =====================================================================
 
def login_page():
    st.set_page_config(page_title="IRONLOG — Login", page_icon="🏋️")
    st.title("🏋️ IRONLOG")
    st.caption("Gym Management Dashboard")
 
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")
        if submitted:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid username or password.")
 
    st.info(f"Demo credentials — Username: `{ADMIN_USERNAME}`  Password: `{ADMIN_PASSWORD}`")
 
 
# =====================================================================
# DASHBOARD
# =====================================================================
 
def dashboard_home():
    st.title("Hello, Admin 👋")
    st.caption("Click any stat below to see the details behind it.")
 
    members = st.session_state.members
    active = [m for m in members if m.active]
    revenue = sum(m.calculate_fee() for m in active)
    trainers = st.session_state.trainers
 
    c1, c2, c3, c4 = st.columns(4)
    if c1.button(f"Total Members: {len(members)}", key="dash_total", use_container_width=True):
        st.session_state.dashboard_view = "total"
    if c2.button(f"Active Members: {len(active)}", key="dash_active", use_container_width=True):
        st.session_state.dashboard_view = "active"
    if c3.button(f"Monthly Revenue: ₹{revenue:,.0f}", key="dash_revenue", use_container_width=True):
        st.session_state.dashboard_view = "revenue"
    if c4.button(f"Trainers: {len(trainers)}", key="dash_trainers", use_container_width=True):
        st.session_state.dashboard_view = "trainers"
 
    view = st.session_state.dashboard_view
    if view:
        st.divider()
        colA, colB = st.columns([8, 1])
        titles = {
            "total": "All Members",
            "active": "Active Members",
            "revenue": "Revenue — Active Members",
            "trainers": "Trainers",
        }
        colA.subheader(titles[view])
        if colB.button("✕ Close", key="close_dash"):
            st.session_state.dashboard_view = None
            st.rerun()
 
        if view == "total":
            for m in members:
                st.write(f"**{m.name}** · {m.membership.plan_name()} · "
                         f"{'🟢 Active' if m.active else '⚪ Inactive'} · ₹{m.calculate_fee():,.0f}")
        elif view == "active":
            if not active:
                st.info("No active members.")
            for m in active:
                st.write(f"**{m.name}** · {m.membership.plan_name()} · ₹{m.calculate_fee():,.0f}")
        elif view == "revenue":
            for m in active:
                st.write(f"**{m.name}** contributes ₹{m.calculate_fee():,.0f} ({m.membership.plan_name()})")
            st.write(f"**Total: ₹{revenue:,.0f}**")
        elif view == "trainers":
            for t in trainers:
                assigned = sum(1 for m in members if t in m.trainers)
                st.write(f"**{t.name}** — {t.specialization}, {t.experience_years} yrs — {assigned} member(s)")
 
 
# =====================================================================
# MEMBERS
# =====================================================================
 
def members_section():
    st.title("Members")
 
    with st.expander("➕ Add New Member"):
        name = st.text_input("Full Name", key="new_member_name")
        plan_choice = st.selectbox("Plan", list(PLAN_CLASSES.keys()), key="new_member_plan")
        cfg = st.session_state.plan_config[plan_choice]
 
        base_fee = st.number_input("Base Fee (₹ / month)", min_value=0,
                                    value=float(cfg["base_fee"]), key="new_member_basefee")
        duration = st.number_input("Duration (months)", min_value=1, value=3, key="new_member_duration")
 
        extra_kwargs = {}
        if plan_choice == "Standard":
            class_fee = st.number_input("Group Class Fee (₹ / month)", min_value=0,
                                         value=float(cfg["class_fee"]), key="new_member_classfee_std")
            extra_kwargs["class_fee"] = class_fee
 
        elif plan_choice == "Premium":
            class_fee = st.number_input("Group Class Fee (₹ / month)", min_value=0,
                                         value=float(cfg["class_fee"]), key="new_member_classfee_prem")
            nutrition_fee = st.number_input("Nutrition Plan Fee (₹ / month)", min_value=0,
                                             value=float(cfg["nutrition_fee"]), key="new_member_nutrition")
            extra_kwargs["class_fee"] = class_fee
            extra_kwargs["nutrition_fee"] = nutrition_fee
 
        elif plan_choice == "Platinum":
            trainer_fee = st.number_input("Trainer Fee (₹ / session)", min_value=0,
                                           value=float(cfg["trainer_fee"]), key="new_member_trainerfee")
            sessions = st.number_input("Sessions / month", min_value=0,
                                        value=int(cfg["sessions"]), key="new_member_sessions")
            extra_kwargs["trainer_fee"] = trainer_fee
            extra_kwargs["sessions_per_month"] = sessions
 
        st.markdown("**Trainer assignment**")
        chosen_trainer_names = []
        all_trainer_names = [t.name for t in st.session_state.trainers]
 
        if plan_choice == "Basic":
            st.caption("Basic plan does not include a trainer.")
 
        elif plan_choice == "Standard":
            pick = st.selectbox("Choose a trainer (optional)", ["None"] + all_trainer_names,
                                 key="new_member_trainer_std")
            if pick != "None":
                chosen_trainer_names.append(pick)
 
        elif plan_choice == "Premium":
            st.caption("Includes trainer: **Rohit** (Boxing)")
            others = [n for n in all_trainer_names if n != "Rohit"]
            pick = st.selectbox("Choose another trainer (optional)", ["None"] + others,
                                 key="new_member_trainer_prem")
            chosen_trainer_names.append("Rohit")
            if pick != "None":
                chosen_trainer_names.append(pick)
 
        elif plan_choice == "Platinum":
            st.caption("Includes trainers: **Rohit** (Boxing), **Sanket** (Stretching & Aerobics)")
            others = [n for n in all_trainer_names if n not in ("Rohit", "Sanket")]
            pick = st.selectbox("Choose another skilled trainer (optional)", ["None"] + others,
                                 key="new_member_trainer_plat")
            chosen_trainer_names.extend(["Rohit", "Sanket"])
            if pick != "None":
                chosen_trainer_names.append(pick)
 
        if st.button("Add Member", key="submit_add_member"):
            if not name.strip():
                st.warning("Enter a name.")
            else:
                membership = PLAN_CLASSES[plan_choice](base_fee, duration, **extra_kwargs)
                trainer_objs = [t for t in (get_trainer_by_name(n) for n in chosen_trainer_names) if t]
                st.session_state.member_counter += 1
                new_id = f"M{st.session_state.member_counter:03d}"
                st.session_state.members.append(GymMember(new_id, name.strip(), membership, trainer_objs))
                st.success(f"Added {name} on the {plan_choice} plan.")
                st.rerun()
 
    st.divider()
 
    search_term = st.text_input("🔍 Search members by name or ID", key="member_search")
    members = st.session_state.members
    if search_term:
        q = search_term.lower()
        filtered = [m for m in members if q in m.name.lower() or q in m.member_id.lower()]
    else:
        filtered = members
 
    if not filtered:
        st.info("No members match your search." if search_term else "No members yet — add one above.")
        return
 
    for m in filtered:
        discount = st.session_state.plan_config[m.membership.plan_name()]["renewal_discount"]
        header = (f"{m.name} — {m.membership.plan_name()} — "
                  f"{'🟢 Active' if m.active else '⚪ Inactive'} — ₹{m.calculate_fee():,.0f}")
 
        with st.expander(header):
            st.write(f"**Member ID:** {m.member_id}")
            st.write(f"**Plan:** {m.membership.plan_name()} — `{m.membership.formula()}`")
            st.write(f"**Base Fee:** ₹{m.membership.base_fee:,.0f}  |  "
                     f"**Duration:** {m.membership.duration_months} months")
            trainer_names = ", ".join(t.name for t in m.trainers) if m.trainers else "None"
            st.write(f"**Trainer(s):** {trainer_names}")
            st.write(f"**Joined:** {m.join_date}")
            st.write(f"**Current Fee:** ₹{m.calculate_fee():,.0f}")
 
            c1, c2, c3 = st.columns(3)
            if c1.button("Renew", key=f"renew_{m.member_id}"):
                m.renew(1)                            # overload #1
                st.rerun()
            if c2.button(f"Renew −{discount}%", key=f"renewd_{m.member_id}"):
                m.renew(1, discount)                  # overload #2
                st.rerun()
            toggle_label = "Cancel Membership" if m.active else "Reactivate Membership"
            if c3.button(toggle_label, key=f"toggle_{m.member_id}"):
                m.active = not m.active
                st.rerun()
 
 
# =====================================================================
# PLANS
# =====================================================================
 
def plans_section():
    st.title("Plans")
    st.write("Every plan is a subclass of the abstract `Membership` class. "
             "Edit fees and the renewal discount for each plan below.")
 
    for plan_name, plan_cls in PLAN_CLASSES.items():
        cfg = st.session_state.plan_config[plan_name]
        sample = plan_cls(0, 1)   # dummy instance — only used to read formula()
 
        with st.expander(f"{plan_name} plan"):
            st.code(sample.formula(), language=None)
 
            new_values = {}
            for field, current in cfg.items():
                label = PLAN_FIELD_LABELS.get(field, field)
                new_values[field] = st.number_input(
                    label, min_value=0, value=current, key=f"planedit_{plan_name}_{field}"
                )
 
            if st.button(f"Save {plan_name} changes", key=f"save_{plan_name}"):
                st.session_state.plan_config[plan_name] = new_values
                st.success(f"{plan_name} plan updated. New members and renewals will use these values.")
                st.rerun()
 
 
# =====================================================================
# TRAINERS
# =====================================================================
 
def trainers_section():
    st.title("Trainers")
 
    with st.expander("➕ Add New Trainer"):
        name = st.text_input("Trainer Name", key="new_trainer_name")
        spec = st.selectbox(
            "Specialization",
            ["Boxing", "Stretching & Aerobics", "Strength", "Cardio", "Yoga", "CrossFit", "Nutrition"],
            key="new_trainer_spec",
        )
        exp = st.number_input("Experience (years)", min_value=0, value=2, key="new_trainer_exp")
 
        if st.button("Add Trainer", key="submit_trainer"):
            if name.strip():
                st.session_state.trainer_counter += 1
                new_id = f"T{st.session_state.trainer_counter:03d}"
                st.session_state.trainers.append(Trainer(new_id, name.strip(), spec, exp))
                st.success(f"Added trainer {name}.")
                st.rerun()
            else:
                st.warning("Enter a name.")
 
    st.divider()
 
    if not st.session_state.trainers:
        st.info("No trainers yet.")
        return
 
    for t in st.session_state.trainers:
        assigned = sum(1 for m in st.session_state.members if t in m.trainers)
        st.write(f"**{t.name}** — {t.specialization}, {t.experience_years} yrs exp — {assigned} member(s) assigned")
 
 
# =====================================================================
# PAYMENTS
# =====================================================================
 
def payments_section():
    st.title("Payments")
 
    with st.expander("➕ Record Payment"):
        members = st.session_state.members
        if members:
            member_choice = st.selectbox("Member", [m.name for m in members], key="pay_member_choice")
            method = st.selectbox("Method", ["Cash", "Card", "UPI"], key="pay_method")
            if st.button("Record Payment", key="submit_payment"):
                m = next(x for x in members if x.name == member_choice)
                st.session_state.payment_counter += 1
                new_id = f"P{st.session_state.payment_counter:03d}"
                st.session_state.payments.append(Payment(new_id, m.member_id, m.calculate_fee(), method))
                st.success("Payment recorded.")
                st.rerun()
        else:
            st.warning("Add a member first.")
 
    st.divider()
 
    search_term = st.text_input("🔍 Search payments by member name or ID", key="payment_search")
    member_lookup = {m.member_id: m.name for m in st.session_state.members}
 
    payments = st.session_state.payments
    if search_term:
        q = search_term.lower()
        filtered = [
            p for p in payments
            if q in p.payment_id.lower()
            or q in p.member_id.lower()
            or q in member_lookup.get(p.member_id, "").lower()
        ]
    else:
        filtered = payments
 
    if not filtered:
        st.info("No payments match your search." if search_term else "No payments yet.")
        return
 
    for p in filtered:
        name = member_lookup.get(p.member_id, "Unknown")
        st.write(f"`{p.payment_id}` — {name} ({p.member_id}) — ₹{p.amount:,.0f} via {p.method} — {p.status}")
 
 
# =====================================================================
# MAIN
# =====================================================================
 
def main():
    if not st.session_state.get("logged_in", False):
        init_state()
        login_page()
        return
 
    st.set_page_config(page_title="IRONLOG", page_icon="🏋️", layout="wide")
    init_state()
 
    with st.sidebar:
        st.title("🏋️ IRONLOG")
        page = st.radio("Navigate", ["Dashboard", "Members", "Plans", "Trainers", "Payments"], key="nav_page")
        st.divider()
        if st.button("Log out", key="logout_btn"):
            st.session_state.logged_in = False
            st.rerun()
 
    if page == "Dashboard":
        dashboard_home()
    elif page == "Members":
        members_section()
    elif page == "Plans":
        plans_section()
    elif page == "Trainers":
        trainers_section()
    elif page == "Payments":
        payments_section()
 
 
if __name__ == "__main__":
    main()
 
