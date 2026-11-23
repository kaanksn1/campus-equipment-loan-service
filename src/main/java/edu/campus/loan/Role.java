package edu.campus.loan;

/** Fixed educational policy from the project proposal, not a real campus policy. */
public enum Role {
    STUDENT(3, 7),
    STAFF(5, 14);

    private final int loanLimit;
    private final int maximumLoanDays;

    Role(int loanLimit, int maximumLoanDays) {
        this.loanLimit = loanLimit;
        this.maximumLoanDays = maximumLoanDays;
    }

    public int loanLimit() {
        return loanLimit;
    }

    public int maximumLoanDays() {
        return maximumLoanDays;
    }
}
