program array_sum_parallel
    use omp_lib
    implicit none
    
    integer :: size, num_threads, i
    integer, allocatable :: numbers(:)
    integer(kind=8) :: sum
    real(kind=8) :: start_time, end_time
    character(len=32) :: arg
    
    ! Get command line arguments
    if (command_argument_count() /= 2) then
        write(*,*) "Usage: ./array_sum_parallel <size> <num_threads>"
        stop
    endif
    
    call get_command_argument(1, arg)
    read(arg, *) size
    call get_command_argument(2, arg)
    read(arg, *) num_threads
    
    allocate(numbers(size))
    
    ! Generate random numbers
    call random_seed()
    do i = 1, size
        call random_number(numbers(i))
        numbers(i) = int(numbers(i) * 100) + 1
    end do
    
    sum = 0
    call omp_set_num_threads(num_threads)
    start_time = omp_get_wtime()
    
    !$omp parallel do reduction(+:sum)
    do i = 1, size
        sum = sum + numbers(i)
    end do
    !$omp end parallel do
    
    end_time = omp_get_wtime()
    
    write(*,*) sum, ",", end_time - start_time
    
    deallocate(numbers)
end program array_sum_parallel 