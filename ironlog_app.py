"""
IRONLOG — Gym Management Dashboard (Streamlit)

This mirrors the C++ OOP mini-project (abstraction, encapsulation,
inheritance, polymorphism, overriding) in Python, since Streamlit apps
run in Python, not C++.

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
    """Abstract base class — ABSTRACTION.
    No plan-level fee formula exists here; only subclasses know it."""

    def __init__(self, base_fee: float, duration_months: int):
        self._base_fee = base_fee              # ENCAPSULATION: "private" by convention
        self._duration_months = duration_months

    # Controlled access to private data (ENCAPSULATION)
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


class Trainer:
    def __init__(self, trainer_id, name, specialization, experience_years):
        self.trainer_id = trainer_id
        self.name = name
        self.specialization = specialization
        self.experience_years = experience_years


class GymMember:
    """Holds a Membership object (composition) — its fee is computed
    POLYMORPHICALLY through whichever subclass was assigned."""

    def __init__(self, member_id, name, membership: Membership, trainer: Trainer = None):
        self.member_id = member_id
        self.name = name
        self.membership = membership
        self.trainer = trainer
        self.active = True
        self.join_date = date.today()

    def calculate_fee(self):
        return self.membership.calculate_fee()   # POLYMORPHISM: correct subclass runs

    def renew(self, extra_months: int, discount_percent: float = 0):
        """Python has no true function overloading (unlike C++'s two
        renewMembership() signatures) — a default parameter approximates it."""
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


# =====================================================================
# APP STATE
# =====================================================================

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "ironlog123"


def init_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "trainers" not in st.session_state:
        t1 = Trainer("T001", "Karan Mehta", "Strength", 5)
        t2 = Trainer("T002", "Divya Rao", "Yoga", 3)
        st.session_state.trainers = [t1, t2]
        st.session_state.trainer_counter = 2

    if "members" not in st.session_state:
        m1 = GymMember("M001", "Rahul Sharma", BasicMembership(1000, 3))
        m2 = GymMember("M002", "Sneha Patil", StandardMembership(1200, 6, 300), st.session_state.trainers[0])
        m3 = GymMember("M003", "Amit Verma", PlatinumMembership(1500, 12, 500, 4), st.session_state.trainers[1])
        st.session_state.members = [m1, m2, m3]
        st.session_state.member_counter = 3

    if "payments" not in st.session_state:
        p1 = Payment("P001", "M002", st.session_state.members[1].calculate_fee(), "UPI")
        p2 = Payment("P002", "M003", st.session_state.members[2].calculate_fee(), "Card")
        st.session_state.payments = [p1, p2]
        st.session_state.payment_counter = 2


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
# DASHBOARD SECTIONS
# =====================================================================

def dashboard_home():
    st.title("Hello, Admin 👋")
    st.caption("Here's what's happening at IRONLOG today.")

    members = st.session_state.members
    active = [m for m in members if m.active]
    revenue = sum(m.calculate_fee() for m in active)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Members", len(members))
    c2.metric("Active Members", len(active))
    c3.metric("Monthly Revenue", f"₹{revenue:,.0f}")
    c4.metric("Trainers", len(st.session_state.trainers))

    st.divider()
    st.subheader("Members Overview")
    for m in members:
        st.write(
            f"**{m.name}** · {m.membership.plan_name()} plan · "
            f"{'🟢 Active' if m.active else '⚪ Inactive'} · ₹{m.calculate_fee():,.0f}"
        )


def members_section():
    st.title("Members")

    with st.expander("➕ Add New Member"):
        with st.form("add_member_form", clear_on_submit=True):
            name = st.text_input("Full Name")
            plan_choice = st.selectbox("Plan", list(PLAN_CLASSES.keys()))
            base_fee = st.number_input("Base Fee (₹ / month)", min_value=0, value=1000)
            duration = st.number_input("Duration (months)", min_value=1, value=3)

            trainer_names = ["None"] + [t.name for t in st.session_state.trainers]
            trainer_choice = st.selectbox("Assign Trainer", trainer_names)

            submitted = st.form_submit_button("Add Member")
            if submitted and name:
                membership = PLAN_CLASSES[plan_choice](base_fee, duration)  # polymorphic creation
                trainer_obj = next((t for t in st.session_state.trainers if t.name == trainer_choice), None)
                st.session_state.member_counter += 1
                new_id = f"M{st.session_state.member_counter:03d}"
                st.session_state.members.append(GymMember(new_id, name, membership, trainer_obj))
                st.success(f"Added {name} on the {plan_choice} plan.")

    st.divider()

    if not st.session_state.members:
        st.info("No members yet — add one above.")
        return

    for m in st.session_state.members:
        cols = st.columns([2, 1.2, 1, 1, 1.2, 1, 1.2])
        cols[0].write(f"**{m.name}**  \n`{m.member_id}`")
        cols[1].write(m.membership.plan_name())       # overriding, shown live
        cols[2].write(f"{m.membership.duration_months} mo")
        cols[3].write("🟢 Active" if m.active else "⚪ Inactive")
        cols[4].write(f"₹{m.calculate_fee():,.0f}")
        if cols[5].button("Renew", key=f"renew_{m.member_id}"):
            m.renew(1)                                  # "overload" call #1
            st.rerun()
        if cols[6].button("Renew −10%", key=f"renewd_{m.member_id}"):
            m.renew(1, 10)                               # "overload" call #2
            st.rerun()


def plans_section():
    st.title("Plans")
    st.write("Every plan is a subclass of the abstract `Membership` class — same interface, different fee formula.")

    sample_args = {
        "Basic": (1000, 1),
        "Standard": (1000, 1, 200),
        "Premium": (1000, 1, 300, 200),
        "Platinum": (1000, 1, 500, 4),
    }

    for plan_name, plan_cls in PLAN_CLASSES.items():
        sample = plan_cls(*sample_args[plan_name])   # properly constructed, no shortcuts
        with st.container(border=True):
            st.subheader(plan_name)
            st.code(sample.formula(), language=None)   # OVERRIDING: each subclass answers differently

    with st.expander("ℹ️ How this maps to OOP"):
        st.markdown(
            "- **Abstraction** — `Membership.calculate_fee()` is declared but never defined at the base level.\n"
            "- **Inheritance** — Basic, Standard, Premium, Platinum all extend `Membership`.\n"
            "- **Overriding** — each subclass supplies its own `calculate_fee()`.\n"
            "- **Polymorphism** — the Members page calls `m.calculate_fee()` without knowing which subclass it is."
        )


def trainers_section():
    st.title("Trainers")

    with st.expander("➕ Add New Trainer"):
        with st.form("add_trainer_form", clear_on_submit=True):
            name = st.text_input("Trainer Name")
            spec = st.selectbox("Specialization", ["Strength", "Cardio", "Yoga", "CrossFit", "Nutrition"])
            exp = st.number_input("Experience (years)", min_value=0, value=2)
            submitted = st.form_submit_button("Add Trainer")
            if submitted and name:
                st.session_state.trainer_counter += 1
                new_id = f"T{st.session_state.trainer_counter:03d}"
                st.session_state.trainers.append(Trainer(new_id, name, spec, exp))
                st.success(f"Added trainer {name}.")

    st.divider()

    if not st.session_state.trainers:
        st.info("No trainers yet.")
        return

    for t in st.session_state.trainers:
        assigned = sum(1 for m in st.session_state.members if m.trainer is t)
        st.write(f"**{t.name}** — {t.specialization}, {t.experience_years} yrs exp — {assigned} member(s) assigned")


def payments_section():
    st.title("Payments")

    with st.expander("➕ Record Payment"):
        members = st.session_state.members
        if members:
            with st.form("add_payment_form", clear_on_submit=True):
                member_choice = st.selectbox("Member", [m.name for m in members])
                method = st.selectbox("Method", ["Cash", "Card", "UPI"])
                submitted = st.form_submit_button("Record Payment")
                if submitted:
                    m = next(x for x in members if x.name == member_choice)
                    st.session_state.payment_counter += 1
                    new_id = f"P{st.session_state.payment_counter:03d}"
                    st.session_state.payments.append(Payment(new_id, m.member_id, m.calculate_fee(), method))
                    st.success("Payment recorded.")
        else:
            st.warning("Add a member first.")

    st.divider()

    if not st.session_state.payments:
        st.info("No payments yet.")
        return

    for p in st.session_state.payments:
        st.write(f"`{p.payment_id}` — {p.member_id} — ₹{p.amount:,.0f} via {p.method} — {p.status}")


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
        page = st.radio("Navigate", ["Dashboard", "Members", "Plans", "Trainers", "Payments"])
        st.divider()
        if st.button("Log out"):
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
