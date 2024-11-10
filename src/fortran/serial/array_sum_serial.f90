program array_sum_serial
    implicit none
    
    integer :: size, i
    REAL, DIMENSION(:), ALLOCATABLE :: numbers
    integer(kind=8) :: sum
    real(kind=8) :: start_time, end_time
    character(len=32) :: arg
    
    ! Get command line arguments
    if (command_argument_count() /= 1) then
        write(*,*) "Usage: ./array_sum_serial <size>"
        stop
    endif
    
    call get_command_argument(1, arg)
    read(arg, *) size
    
    allocate(numbers(size))
    
    ! Generate random numbers
    call random_seed()
    do i = 1, size
        call random_number(numbers(i))
        numbers(i) = int(numbers(i) * 100) + 1
    end do
    
    sum = 0
    call cpu_time(start_time)
    
    do i = 1, size
        sum = sum + numbers(i)
    end do
    
    call cpu_time(end_time)
    
    write(*,*) sum, ",", end_time - start_time
    
    deallocate(numbers)
end program array_sum_serial 