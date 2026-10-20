import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { zodResolver } from '@hookform/resolvers/zod'
import { useFieldArray, useForm } from 'react-hook-form'
import { z } from 'zod'
import { Dumbbell, LogOut, Plus, Search, Trash2 } from 'lucide-react'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import EmptyState from '../../components/ui/EmptyState'
import Input from '../../components/ui/Input'
import Modal from '../../components/ui/Modal'
import Spinner from '../../components/ui/Spinner'
import { supabase } from '../../config/supabase'
import {
  createWorkoutPlan,
  deleteWorkoutPlan,
  getWorkoutOptions,
  getWorkoutPlans,
  getWorkoutUser,
  updateWorkoutPlan,
} from './api'

const loginSchema = z.object({
  email: z.string().email('Enter a valid email address.'),
  password: z.string().min(1, 'Enter your password.'),
})

const exerciseSchema = z.object({
  workout_day: z.string().trim().min(1, 'Enter a workout day.').max(50),
  exercise_name: z.string().trim().min(1, 'Enter an exercise name.').max(200),
  muscle_group: z.string().max(100),
  sets: z.string().refine((value) => !value || (/^\d+$/.test(value) && Number(value) > 0), {
    message: 'Sets must be a positive whole number.',
  }),
  reps: z.string().max(50),
  duration: z.string().max(50),
  rest_time: z.string().max(50),
  instructions: z.string(),
})

const planSchema = z.object({
  member_id: z.string().min(1, 'Select a member.'),
  trainer_id: z.string().min(1, 'Select a trainer.'),
  title: z.string().trim().min(1, 'Enter a plan title.').max(200),
  notes: z.string(),
  exercises: z.array(exerciseSchema).min(1, 'Add at least one exercise.').max(100),
})

const emptyExercise = {
  workout_day: '',
  exercise_name: '',
  muscle_group: '',
  sets: '',
  reps: '',
  duration: '',
  rest_time: '',
  instructions: '',
}

function displayError(error) {
  return error?.message || 'Something went wrong. Please try again.'
}

function SignInForm() {
  const [error, setError] = useState('')
  const form = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  })

  async function onSubmit(values) {
    setError('')
    try {
      const { error: signInError } = await supabase.auth.signInWithPassword(values)
      if (signInError) throw new Error(signInError.message)
    } catch (signInError) {
      setError(displayError(signInError))
    }
  }

  return (
    <main className="min-h-screen bg-surface-900 px-4 py-12 text-gray-100">
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="mx-auto mt-12 flex max-w-md flex-col gap-5 rounded-2xl border border-surface-700 bg-surface-800 p-6 sm:p-8"
      >
        <div>
          <p className="text-sm font-semibold uppercase tracking-widest text-brand-400">RV Fitness</p>
          <h1 className="mt-2 text-2xl font-bold text-white">Sign in to view workout plans</h1>
          <p className="mt-2 text-sm text-gray-400">Use your gym account to continue.</p>
        </div>
        <Input
          label="Email"
          type="email"
          autoComplete="email"
          error={form.formState.errors.email?.message}
          {...form.register('email')}
        />
        <Input
          label="Password"
          type="password"
          autoComplete="current-password"
          error={form.formState.errors.password?.message}
          {...form.register('password')}
        />
        {error && <p role="alert" className="text-sm text-red-400">{error}</p>}
        <Button type="submit" isLoading={form.formState.isSubmitting} className="w-full">
          Sign in
        </Button>
      </form>
    </main>
  )
}

function WorkoutPlanForm({ plan, user, options, onClose, onSave, isSaving, error }) {
  const form = useForm({
    resolver: zodResolver(planSchema),
    defaultValues: {
      member_id: plan?.member_id || '',
      trainer_id: plan?.trainer_id || (user.role === 'trainer' ? user.trainer_id : ''),
      title: plan?.title || '',
      notes: plan?.notes || '',
      exercises: plan?.exercises?.map((exercise) => ({
        workout_day: exercise.workout_day,
        exercise_name: exercise.exercise_name,
        muscle_group: exercise.muscle_group || '',
        sets: exercise.sets ? String(exercise.sets) : '',
        reps: exercise.reps || '',
        duration: exercise.duration || '',
        rest_time: exercise.rest_time || '',
        instructions: exercise.instructions || '',
      })) || [{ ...emptyExercise }],
    },
  })
  const { fields, append, remove } = useFieldArray({ control: form.control, name: 'exercises' })
  const formErrors = form.formState.errors

  function submit(values) {
    onSave({
      ...values,
      notes: values.notes.trim() || null,
      trainer_id: user.role === 'trainer' ? user.trainer_id : values.trainer_id,
      exercises: values.exercises.map((exercise) => ({
        ...exercise,
        muscle_group: exercise.muscle_group.trim() || null,
        sets: exercise.sets ? Number(exercise.sets) : null,
        reps: exercise.reps.trim() || null,
        duration: exercise.duration.trim() || null,
        rest_time: exercise.rest_time.trim() || null,
        instructions: exercise.instructions.trim() || null,
      })),
    })
  }

  return (
    <Modal isOpen onClose={onClose} title={plan ? 'Edit workout plan' : 'Create workout plan'} size="xl">
      <form onSubmit={form.handleSubmit(submit)} className="max-h-[75vh] space-y-5 overflow-y-auto pr-1">
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="flex flex-col gap-1.5 text-sm font-medium text-gray-300">
            Member
            <select
              className="w-full rounded-lg border border-surface-500 bg-surface-700 px-4 py-2.5 text-sm text-gray-100"
              {...form.register('member_id')}
            >
              <option value="">Select a member</option>
              {options.members.map((member) => (
                <option key={member.id} value={member.id}>
                  {member.member_code} — {member.full_name}
                </option>
              ))}
            </select>
            {formErrors.member_id && <span className="text-xs text-red-400">{formErrors.member_id.message}</span>}
          </label>
          {user.role === 'admin' && (
            <label className="flex flex-col gap-1.5 text-sm font-medium text-gray-300">
              Trainer
              <select
                className="w-full rounded-lg border border-surface-500 bg-surface-700 px-4 py-2.5 text-sm text-gray-100"
                {...form.register('trainer_id')}
              >
                <option value="">Select a trainer</option>
                {options.trainers.map((trainer) => (
                  <option key={trainer.id} value={trainer.id}>{trainer.full_name}</option>
                ))}
              </select>
              {formErrors.trainer_id && <span className="text-xs text-red-400">{formErrors.trainer_id.message}</span>}
            </label>
          )}
          <Input label="Plan title" error={formErrors.title?.message} {...form.register('title')} />
          <label className="flex flex-col gap-1.5 text-sm font-medium text-gray-300 sm:col-span-2">
            Notes
            <textarea
              rows="3"
              className="w-full rounded-lg border border-surface-500 bg-surface-700 px-4 py-2.5 text-sm text-gray-100"
              {...form.register('notes')}
            />
          </label>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between gap-3">
            <h3 className="font-semibold text-white">Exercises</h3>
            <Button type="button" variant="outline" size="sm" onClick={() => append({ ...emptyExercise })}>
              <Plus className="h-4 w-4" /> Add exercise
            </Button>
          </div>
          {formErrors.exercises?.root?.message && (
            <p className="text-sm text-red-400">{formErrors.exercises.root.message}</p>
          )}
          {fields.map((field, index) => {
            const errors = formErrors.exercises?.[index]
            return (
              <div key={field.id} className="space-y-3 rounded-xl border border-surface-700 bg-surface-900/50 p-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-brand-300">Exercise {index + 1}</h4>
                  {fields.length > 1 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      aria-label={`Remove exercise ${index + 1}`}
                      onClick={() => remove(index)}
                    >
                      <Trash2 className="h-4 w-4 text-red-400" />
                    </Button>
                  )}
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  <Input label="Day" placeholder="Monday" error={errors?.workout_day?.message} {...form.register(`exercises.${index}.workout_day`)} />
                  <Input label="Exercise" placeholder="Squats" error={errors?.exercise_name?.message} {...form.register(`exercises.${index}.exercise_name`)} />
                  <Input label="Muscle group" {...form.register(`exercises.${index}.muscle_group`)} />
                  <Input label="Sets" type="number" min="1" error={errors?.sets?.message} {...form.register(`exercises.${index}.sets`)} />
                  <Input label="Reps" placeholder="10-12" {...form.register(`exercises.${index}.reps`)} />
                  <Input label="Duration" placeholder="30 min" {...form.register(`exercises.${index}.duration`)} />
                  <Input label="Rest time" placeholder="60 sec" {...form.register(`exercises.${index}.rest_time`)} />
                  <Input label="Instructions" {...form.register(`exercises.${index}.instructions`)} />
                </div>
              </div>
            )
          })}
        </div>

        {error && <p role="alert" className="text-sm text-red-400">{error}</p>}
        <Modal.Footer>
          <Button type="button" variant="ghost" onClick={onClose}>Cancel</Button>
          <Button type="submit" isLoading={isSaving}>{plan ? 'Save changes' : 'Create plan'}</Button>
        </Modal.Footer>
      </form>
    </Modal>
  )
}

export default function WorkoutsPage() {
  const [session, setSession] = useState(undefined)
  const authLoading = session === undefined
  const isAuthenticated = Boolean(session)
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [selectedPlan, setSelectedPlan] = useState(undefined)
  const [formError, setFormError] = useState('')
  const [notice, setNotice] = useState('')
  const pageSize = 8

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session: currentSession } }) => {
      setSession(currentSession)
    })
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession)
    })
    return () => subscription.unsubscribe()
  }, [])

  const userQuery = useQuery({
    queryKey: ['workout-user', session?.user?.id],
    queryFn: getWorkoutUser,
    enabled: isAuthenticated,
    retry: false,
  })
  const user = userQuery.data
  const isManager = user?.role === 'admin' || user?.role === 'trainer'

  const optionsQuery = useQuery({
    queryKey: ['workout-options', user?.id],
    queryFn: getWorkoutOptions,
    enabled: isManager,
    retry: false,
  })
  const plansQuery = useQuery({
    queryKey: ['workout-plans', user?.id, page, pageSize, search],
    queryFn: () => getWorkoutPlans({ page, pageSize, search }),
    enabled: Boolean(user),
    retry: false,
  })

  const saveMutation = useMutation({
    mutationFn: (payload) => selectedPlan
      ? updateWorkoutPlan({ id: selectedPlan.id, ...payload })
      : createWorkoutPlan(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['workout-plans'] })
      setSelectedPlan(undefined)
      setFormError('')
      setNotice('Workout plan saved.')
    },
    onError: (error) => setFormError(displayError(error)),
  })
  const deleteMutation = useMutation({
    mutationFn: deleteWorkoutPlan,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['workout-plans'] })
      if (page > 1 && plans.length === 1) setPage(page - 1)
      setNotice('Workout plan deleted.')
    },
  })

  function searchPlans(event) {
    event.preventDefault()
    setPage(1)
    setSearch(searchInput.trim())
  }

  function startPlanEdit(plan) {
    setFormError('')
    setNotice('')
    setSelectedPlan(plan)
  }

  function deletePlan(plan) {
    if (!window.confirm(`Delete the workout plan "${plan.title}"? Its exercises will also be removed.`)) return
    setNotice('')
    deleteMutation.mutate(plan.id)
  }

  async function handleSignOut() {
    const { error } = await supabase.auth.signOut()
    if (error) setNotice(error.message)
  }

  if (authLoading) {
    return <div className="flex min-h-screen items-center justify-center"><Spinner size="lg" /></div>
  }
  if (!isAuthenticated) return <SignInForm />
  if (userQuery.isLoading) {
    return <div className="flex min-h-screen items-center justify-center"><Spinner size="lg" /></div>
  }
  if (userQuery.isError) {
    return (
      <main className="min-h-screen bg-surface-900 p-6 text-gray-100">
        <div className="mx-auto max-w-3xl rounded-xl border border-red-900 bg-red-950/40 p-5" role="alert">
          <p>{displayError(userQuery.error)}</p>
          <Button variant="ghost" className="mt-3" onClick={handleSignOut}>Sign out</Button>
        </div>
      </main>
    )
  }

  const plans = plansQuery.data?.items || []
  const total = plansQuery.data?.total || 0
  const pageCount = Math.max(1, Math.ceil(total / pageSize))

  return (
    <main className="min-h-screen bg-surface-900 px-4 py-8 text-gray-100 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest text-brand-400">RV Fitness</p>
            <h1 className="mt-1 text-3xl font-bold text-white">Workout plans</h1>
            <p className="mt-2 text-sm text-gray-400">Welcome, {user.full_name}</p>
          </div>
          <div className="flex items-center gap-3">
            {isManager && (
              <Button disabled={!optionsQuery.data} onClick={() => startPlanEdit(null)}>
                <Plus className="h-4 w-4" /> New plan
              </Button>
            )}
            <Button variant="ghost" onClick={handleSignOut} aria-label="Sign out">
              <LogOut className="h-4 w-4" /> <span className="hidden sm:inline">Sign out</span>
            </Button>
          </div>
        </header>

        <form onSubmit={searchPlans} className="mb-6 flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
            <input
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="Search plans or members"
              aria-label="Search workout plans"
              className="w-full rounded-lg border border-surface-600 bg-surface-800 py-2.5 pl-10 pr-4 text-sm text-white placeholder:text-gray-500"
            />
          </div>
          <Button type="submit" variant="secondary">Search</Button>
        </form>

        {notice && <p role="status" className="mb-4 text-sm text-green-400">{notice}</p>}
        {deleteMutation.isError && (
          <p role="alert" className="mb-4 text-sm text-red-400">{displayError(deleteMutation.error)}</p>
        )}
        {optionsQuery.isError && (
          <p role="alert" className="mb-4 text-sm text-red-400">{displayError(optionsQuery.error)}</p>
        )}
        {plansQuery.isError && (
          <div role="alert" className="mb-4 rounded-lg border border-red-900 bg-red-950/40 p-4 text-sm text-red-300">
            {displayError(plansQuery.error)}
            <Button variant="ghost" size="sm" onClick={() => plansQuery.refetch()}>Try again</Button>
          </div>
        )}
        {plansQuery.isLoading ? (
          <div className="flex justify-center py-20"><Spinner size="lg" /></div>
        ) : plansQuery.isError ? null : plans.length === 0 ? (
          <Card>
            <EmptyState
              icon={Dumbbell}
              title="No workout plans found"
              description={search ? 'Try another search, or clear the search to see all plans.' : 'Workout plans assigned to you will appear here.'}
              action={isManager && !search ? <Button disabled={!optionsQuery.data} onClick={() => startPlanEdit(null)}>Create a plan</Button> : null}
            />
          </Card>
        ) : (
          <div className="grid gap-4 lg:grid-cols-2">
            {plans.map((plan) => (
              <Card key={plan.id}>
                <Card.Header className="flex items-start justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-semibold text-white">{plan.title}</h2>
                    <p className="mt-1 text-sm text-gray-400">
                      {plan.member_code} · {plan.member_name}
                    </p>
                  </div>
                  {isManager && (
                    <div className="flex shrink-0 gap-1">
                      <Button variant="ghost" size="sm" onClick={() => startPlanEdit(plan)}>Edit</Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        disabled={deleteMutation.isPending}
                        onClick={() => deletePlan(plan)}
                      >
                        <Trash2 className="h-4 w-4 text-red-400" />
                        <span className="sr-only">Delete {plan.title}</span>
                      </Button>
                    </div>
                  )}
                </Card.Header>
                <Card.Body>
                  {plan.notes && <p className="mb-4 whitespace-pre-wrap text-sm text-gray-400">{plan.notes}</p>}
                  <ul className="space-y-3">
                    {plan.exercises.map((exercise) => (
                      <li key={exercise.id} className="rounded-lg bg-surface-700/70 p-3">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <h3 className="font-medium text-white">{exercise.exercise_name}</h3>
                          <span className="rounded-full bg-brand-500/15 px-2.5 py-1 text-xs font-medium text-brand-300">{exercise.workout_day}</span>
                        </div>
                        <p className="mt-1 text-sm text-gray-400">
                          {[exercise.muscle_group, exercise.sets && `${exercise.sets} sets`, exercise.reps && `${exercise.reps} reps`, exercise.duration, exercise.rest_time && `Rest ${exercise.rest_time}`]
                            .filter(Boolean)
                            .join(' · ') || 'Details not specified'}
                        </p>
                        {exercise.instructions && <p className="mt-2 text-sm text-gray-300">{exercise.instructions}</p>}
                      </li>
                    ))}
                  </ul>
                </Card.Body>
              </Card>
            ))}
          </div>
        )}

        {total > pageSize && (
          <nav aria-label="Workout plan pages" className="mt-8 flex items-center justify-center gap-4">
            <Button variant="secondary" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</Button>
            <span className="text-sm text-gray-400">Page {page} of {pageCount}</span>
            <Button variant="secondary" size="sm" disabled={page >= pageCount} onClick={() => setPage(page + 1)}>Next</Button>
          </nav>
        )}
      </div>

      {selectedPlan !== undefined && optionsQuery.data && (
        <WorkoutPlanForm
          key={selectedPlan?.id || 'new'}
          plan={selectedPlan}
          user={user}
          options={optionsQuery.data}
          onClose={() => {
            setSelectedPlan(undefined)
            setFormError('')
          }}
          onSave={(payload) => saveMutation.mutate(payload)}
          isSaving={saveMutation.isPending}
          error={formError}
        />
      )}
      {selectedPlan !== undefined && optionsQuery.isLoading && (
        <Modal isOpen onClose={() => setSelectedPlan(undefined)} title="Loading form">
          <div className="flex justify-center py-8"><Spinner /></div>
        </Modal>
      )}
    </main>
  )
}
