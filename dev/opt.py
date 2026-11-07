"""Exaktes Optimum der 2D-Behälterpackung (Rechtecke ohne Drehung) mit CP-SAT (ortools) und NoOverlap2D: nur für Generator und Tests, nie für die App.

Zuordnungsmodell: Jedes Rechteck liegt in genau einem von B Behältern, in jedem Behälter überlappen sich die Rechtecke nicht; Behälter werden der Reihe nach benutzt, das erste Rechteck
liegt im ersten Behälter (Symmetrie). Minimiert wird die Zahl der benutzten Behälter."""


def optimum_cpsat(rects, cap: int, obergrenze: int, zeitlimit: float = 60.0, arbeiter: int = 4):
    """Kleinste Behälterzahl bis zur Obergrenze (eine gefundene Packung); -1, wenn das Zeitlimit erreicht wird, ohne dass das Optimum bewiesen ist."""
    from ortools.sat.python import cp_model

    n = len(rects)
    if n == 0:
        return 0
    B = obergrenze
    m = cp_model.CpModel()
    benutzt = [m.NewBoolVar(f"u{b}") for b in range(B)]
    iv_x = {b: [] for b in range(B)}
    iv_y = {b: [] for b in range(B)}
    in_bin = {}
    for i, (w, h) in enumerate(rects):
        lits = []
        for b in range(B):
            p = m.NewBoolVar(f"p{i}_{b}")
            x = m.NewIntVar(0, cap - w, f"x{i}_{b}")
            y = m.NewIntVar(0, cap - h, f"y{i}_{b}")
            iv_x[b].append(m.NewOptionalFixedSizeIntervalVar(x, w, p, f"ix{i}_{b}"))
            iv_y[b].append(m.NewOptionalFixedSizeIntervalVar(y, h, p, f"iy{i}_{b}"))
            m.AddImplication(p, benutzt[b])
            lits.append(p)
            in_bin[(i, b)] = p
        m.AddExactlyOne(lits)
    for b in range(B):
        m.AddNoOverlap2D(iv_x[b], iv_y[b])
    for b in range(B - 1):
        m.AddImplication(benutzt[b + 1], benutzt[b])
    m.Add(in_bin[(0, 0)] == 1)
    m.Minimize(sum(benutzt))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = zeitlimit
    s.parameters.num_workers = arbeiter
    s.parameters.random_seed = 1
    status = s.Solve(m)
    if status == cp_model.OPTIMAL:
        return int(round(s.ObjectiveValue()))
    return -1
