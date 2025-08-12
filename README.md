# Sports Scheduling for Amateur Leagues

This project was developed for the *Linear & Combinatorial Optimization* course in the 8th semester of the Electrical and Computer Engineering Department at the University of Patras. It addresses the well-known *Sports Scheduling Problem* using the example of an amateur football tournament. This problem involves the manual creation of a tournament's match schedule, which is a time-consuming process that often produces inefficient results.

To tackle this issue, I modeled the scheduling process as a Linear Programming problem and implemented a solution using Python’s PuLP library. The created application fully automates the task, generating optimal match schedules in under 1 second, significantly reducing planning time while aiming to meet the needs of both:

<ul>
<li>Tournament organizers</li>
<li>Tournament players</li>
</ul>

in the best way possible.

<br/>

## Dependencies & Running the Application

To run the application, ensure the following:

- The libraries `pulp` and `timeit` are installed.
- When running `problem-x.py` (the application for a tournament with *x* teams), ensure it is located in the same folder as the `availability-x.txt` file.

<br/>

## Supporting Files

Additional resources and documentation can be found in:

- `Report_Greek.pdf`: A detailed report in Greek that defines the problem, models it with Linear Programming, implements it in Python, and analyzes performance through test runs.
- `Presentation_Greek.pptx`: A Greek presentation showcasing the tournament case study, problem modeling, results, and conclusions.
- `Presentation_English.pptx`: An English presentation showcasing the tournament case study, problem modeling, results, and conclusions.

<br/>

---

<br/>

**George Tsialios**
