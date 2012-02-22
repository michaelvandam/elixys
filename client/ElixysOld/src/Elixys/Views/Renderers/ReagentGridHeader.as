package Elixys.Views.Renderers
{
	import flash.display.DisplayObject;
	
	import spark.components.Label;
	import spark.skins.spark.DefaultGridHeaderRenderer;
	
	public class ReagentGridHeader extends DefaultGridHeaderRenderer
	{
		/***
		 * Member variables
		 **/
		
		// Constructor
		public function ReagentGridHeader()
		{
			super();
		}

		// Prepare to render
		override public function prepare(hasBeenRecycled:Boolean):void
		{
			// Call the base implementation
			super.prepare(hasBeenRecycled);

			// Call prepare() on our children
			for (var i:uint = 0; i < numChildren; ++i)
			{
				var pRenderer:DefaultGridHeaderRenderer = getChildAt(i) as DefaultGridHeaderRenderer;
				if (pRenderer != null)
				{
					pRenderer.prepare(hasBeenRecycled);
				}
			}
		}
	}
}