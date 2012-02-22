package Elixys.Views.Renderers
{
	import spark.components.Label;
	import spark.skins.spark.DefaultGridHeaderRenderer;
	
	public class ReagentGridHeaderChild extends DefaultGridHeaderRenderer
	{
		/***
		 * Member functions
		 **/
		
		// Constructor
		public function ReagentGridHeaderChild()
		{
			super();
		}

		// Prepare to render
		override public function prepare(hasBeenRecycled:Boolean):void
		{
			// Set our label as our ID
			label = id;
			
			// Call the base implementation
			super.prepare(hasBeenRecycled);
		}
	}
}