import { MdFastForward, MdFastRewind } from "react-icons/md";
import { CaretRightIcon } from "../../../../../../common/components/icons";

export const MAX_DISPLAY_SHAPES = 10;

export const Paginator = ({
  page,
  setPage,
  maxPage,
  maxShapes,
}: {
  page: number;
  setPage: (page: number) => void;
  maxPage: number;
  maxShapes: number;
}) => {
  const coreCss =
    "flex items-center justify-center w-8 h-8 rounded-full bg-gray-600 hover:bg-gray-500 ";
  const leftBtnCls =
    coreCss + (page === 0 ? "text-gray-500 hover:bg-transparent" : "");
  const rightBtnCls =
    coreCss + (page === maxPage ? "text-gray-500 hover:bg-transparent" : "");

  return (
    <div className="flex items-center justify-center w-full">
      <button className={leftBtnCls} onClick={() => setPage(0)}>
        <MdFastRewind />
      </button>
      <button
        className={leftBtnCls}
        onClick={() => setPage(Math.max(0, page - 1))}
      >
        <CaretRightIcon className="w-4 h-4 transform rotate-180" />
      </button>
      <div className="mx-2 select-none">
        {page * MAX_DISPLAY_SHAPES + 1} -{" "}
        {Math.min(MAX_DISPLAY_SHAPES + page * MAX_DISPLAY_SHAPES, maxShapes)}
      </div>
      <button
        className={rightBtnCls}
        onClick={() => setPage(Math.min(maxPage, page + 1))}
      >
        <CaretRightIcon className="w-4 h-4" />
      </button>
      <button className={rightBtnCls} onClick={() => setPage(maxPage)}>
        <MdFastForward />
      </button>
    </div>
  );
};
