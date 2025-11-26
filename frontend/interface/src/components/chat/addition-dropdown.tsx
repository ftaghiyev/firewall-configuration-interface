import { LuPlus } from "react-icons/lu";
import { Button } from "../ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import AskContextDialog from "./ask-context-dialog";

type AdditionDropdownProps = {
  open?: boolean;
  setOpen?: (open: boolean) => void;
  children?: React.ReactNode;
};

function AdditionDropdown({ open, setOpen, children }: AdditionDropdownProps) {
  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        {children ?? (
          <Button variant="ghost" size="icon" className="self-end">
            <LuPlus className="size-5" />
          </Button>
        )}
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuLabel>Options</DropdownMenuLabel>
        <DropdownMenuGroup>
          <DropdownMenuItem asChild>
            <AskContextDialog />
          </DropdownMenuItem>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export default AdditionDropdown;
